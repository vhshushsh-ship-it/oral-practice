from fastapi import APIRouter, HTTPException, Depends

from db import get_db, release_db
from models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
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
)

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
        if not user or not verify_password(body.password, user["password_hash"]):
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
