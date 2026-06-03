import uuid
import random
import bcrypt
from datetime import datetime, timedelta, timezone

import aiomysql
from jose import jwt, JWTError

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS, VERIFICATION_CODE_TTL


# ====================== 密码哈希 ======================
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))


# ====================== JWT ======================
def create_access_token(user_id: str, email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# ====================== 验证码生成 ======================
def generate_verification_code() -> str:
    """生成 6 位随机数字验证码"""
    return f"{random.randint(0, 999999):06d}"


# ====================== 用户 CRUD ======================
async def create_user(db, email: str, password: str, email_verified: bool = False) -> dict:
    """创建新用户，返回不含密码的用户字典"""
    user_id = f"user-{uuid.uuid4().hex[:12]}"
    password_hash = hash_password(password)
    verified = 1 if email_verified else 0
    async with db.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            "INSERT INTO users (id, email, password_hash, email_verified) VALUES (%s, %s, %s, %s)",
            (user_id, email, password_hash, verified),
        )
        await db.commit()
        await cur.execute(
            "SELECT id, email, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        return await cur.fetchone()


async def get_user_by_email(db, email: str) -> dict | None:
    """根据邮箱查找用户，包含密码哈希"""
    async with db.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = %s",
            (email,),
        )
        return await cur.fetchone()


async def get_user_by_id(db, user_id: str) -> dict | None:
    """根据ID查找用户，不含密码哈希"""
    async with db.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            "SELECT id, email, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        return await cur.fetchone()


# ====================== 验证码 CRUD ======================
async def create_verification_code(db, email: str, code: str, purpose: str) -> None:
    """存储验证码到数据库"""
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=VERIFICATION_CODE_TTL)
    async with db.cursor() as cur:
        # 先废弃该邮箱同一用途的旧验证码
        await cur.execute(
            "UPDATE verification_codes SET used = 1 WHERE email = %s AND purpose = %s AND used = 0",
            (email, purpose),
        )
        # 插入新验证码
        await cur.execute(
            "INSERT INTO verification_codes (email, code, purpose, expires_at) VALUES (%s, %s, %s, %s)",
            (email, code, purpose, expires_at),
        )
        await db.commit()


async def verify_code(db, email: str, code: str, purpose: str) -> dict | None:
    """
    校验验证码。成功返回验证码记录 dict，失败返回 None。
    会自动更新 attempts 计数，超过 5 次尝试则作废验证码。
    """
    async with db.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            """SELECT id, email, code, purpose, expires_at, used, attempts, created_at
               FROM verification_codes
               WHERE email = %s AND purpose = %s AND used = 0
               ORDER BY created_at DESC LIMIT 1""",
            (email, purpose),
        )
        row = await cur.fetchone()
        if not row:
            return None

        # 检查是否过期（MySQL DATETIME 无时区信息，需补齐 UTC 后再比较）
        expires_at = row["expires_at"].replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            await cur.execute(
                "UPDATE verification_codes SET used = 1 WHERE id = %s",
                (row["id"],),
            )
            return None

        # 检查尝试次数
        if row["attempts"] >= 5:
            await cur.execute(
                "UPDATE verification_codes SET used = 1 WHERE id = %s",
                (row["id"],),
            )
            return None

        # 验证码不匹配
        if row["code"] != code:
            await cur.execute(
                "UPDATE verification_codes SET attempts = attempts + 1 WHERE id = %s",
                (row["id"],),
            )
            return None

        # 验证成功，标记已使用
        await cur.execute(
            "UPDATE verification_codes SET used = 1 WHERE id = %s",
            (row["id"],),
        )
        await db.commit()
        return row
