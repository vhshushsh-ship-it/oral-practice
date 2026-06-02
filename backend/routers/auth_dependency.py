from fastapi import HTTPException, Header

from services.auth_service import decode_access_token


async def get_current_user(authorization: str = Header(None)) -> str:
    """从 Authorization header 提取 JWT 并返回 user_id"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    token = authorization[len("Bearer "):]
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]


async def get_optional_user(authorization: str = Header(None)) -> str | None:
    """可选认证：有 token 则返回 user_id，没有则返回 None"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[len("Bearer "):]
    payload = decode_access_token(token)
    return payload["sub"] if payload else None
