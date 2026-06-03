import asyncio

from fastapi import APIRouter, HTTPException, Depends

from db import get_db, release_db
from models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    SendCodeRequest,
    VerifyCodeRequest,
    TokenResponse,
    UserResponse,
)
from routers.auth_dependency import get_current_user
from services.auth_service import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    create_access_token,
    verify_password,
    generate_verification_code,
    create_verification_code,
    verify_code,
)
from services.email_service import (
    send_verification_code_email,
    check_cooldown,
    record_send,
)
from config import VERIFICATION_CODE_COOLDOWN

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(body: UserRegisterRequest):
    db = await get_db()
    try:
        existing = await get_user_by_email(db, body.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        user = await create_user(db, body.email, body.password)
        token = create_access_token(user["id"], user["email"])
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                created_at=str(user["created_at"]),
            ),
        )
    finally:
        await release_db(db)


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLoginRequest):
    db = await get_db()
    try:
        user = await get_user_by_email(db, body.email)
        if not user or not user["password_hash"] or not verify_password(body.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        token = create_access_token(user["id"], user["email"])
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                created_at=str(user["created_at"]),
            ),
        )
    finally:
        await release_db(db)


# ====================== 邮箱验证码认证（仅用于注册）======================

@router.post("/send-code")
async def send_code(body: SendCodeRequest):
    """发送注册验证码到邮箱"""
    import traceback

    # ---- 冷却检查 ----
    remaining = check_cooldown(body.email, VERIFICATION_CODE_COOLDOWN)
    if remaining is not None:
        raise HTTPException(
            status_code=429,
            detail=f"发送过于频繁，请 {remaining} 秒后再试",
        )

    db = await get_db()
    try:
        # ---- 检查邮箱是否已注册 ----
        existing = await get_user_by_email(db, body.email)
        if existing:
            raise HTTPException(status_code=409, detail="该邮箱已注册，请直接登录")

        # ---- 生成并存储验证码 ----
        purpose = "register"
        code = generate_verification_code()
        await create_verification_code(db, body.email, code, purpose)

        # ---- 异步发送邮件 ----
        loop = asyncio.get_running_loop()
        try:
            await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    send_verification_code_email,
                    body.email,
                    code,
                    purpose,
                ),
                timeout=15.0,
            )
        except asyncio.TimeoutError:
            print(f"[SEND CODE] SMTP timeout for {body.email}")
            raise HTTPException(status_code=500, detail="邮件发送超时，请稍后重试")
        except RuntimeError as e:
            print(f"[SEND CODE] SMTP error for {body.email}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

        record_send(body.email)

        print(f"[SEND CODE] Verification code sent to {body.email} for register")
        return {"message": "验证码已发送，请查收邮件"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[SEND CODE ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="验证码发送失败，请稍后重试")
    finally:
        await release_db(db)


@router.post("/verify-code", response_model=TokenResponse)
async def verify_code_endpoint(body: VerifyCodeRequest):
    """验证邮箱验证码 + 密码，完成注册，返回 JWT Token"""
    import traceback

    # ---- 前后端双重校验：两次密码必须一致 ----
    if body.password != body.confirm_password:
        raise HTTPException(status_code=400, detail="两次输入的密码不一致")

    # 密码长度校验（Pydantic 已校验 min_length=6，此处做二次保障）
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度至少为6位")

    db = await get_db()
    try:
        # ---- 验证码校验 ----
        code_record = await verify_code(db, body.email, body.code, "register")
        if code_record is None:
            raise HTTPException(status_code=400, detail="验证码错误或已过期")

        # ---- 注册：创建用户（带密码 + 邮箱已验证） ----
        user = await create_user(db, body.email, body.password, email_verified=True)

        # ---- 签发 JWT ----
        token = create_access_token(user["id"], user["email"])

        print(f"[VERIFY CODE] User {user['email']} registered via verification code")

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                created_at=str(user["created_at"]),
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[VERIFY CODE ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"验证失败: {type(e).__name__}: {e}")
    finally:
        await release_db(db)


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user)):
    db = await get_db()
    try:
        user = await get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(
            id=user["id"],
            email=user["email"],
            created_at=str(user["created_at"]),
        )
    finally:
        await release_db(db)
