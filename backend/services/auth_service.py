import uuid
import bcrypt
from datetime import datetime, timedelta, timezone

import aiomysql
from jose import jwt, JWTError

from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_HOURS


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


# ====================== 用户 CRUD ======================
async def create_user(db, email: str, password: str) -> dict:
    """创建新用户，返回不含密码的用户字典"""
    user_id = f"user-{uuid.uuid4().hex[:12]}"
    password_hash = hash_password(password)
    async with db.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(
            "INSERT INTO users (id, email, password_hash) VALUES (%s, %s, %s)",
            (user_id, email, password_hash),
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
