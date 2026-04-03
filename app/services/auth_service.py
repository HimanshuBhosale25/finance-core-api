from datetime import timezone

import redis as redis_lib
from jose import jwt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.models.user import User, UserStatus
from app.schemas.auth import LoginRequest


def register_user(db: Session, name: str, email: str, password: str) -> User:
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, payload: LoginRequest) -> str:
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if user.status == UserStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Contact an admin.",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return token


def logout_user(token: str, redis: redis_lib.Redis) -> None:
    try:
        payload = decode_access_token(token)
        exp = payload.get("exp")
        if exp:
            from datetime import datetime
            now = int(datetime.now(timezone.utc).timestamp())
            ttl = exp - now
            if ttl > 0:
                redis.setex(f"blacklist:{token}", ttl, "1")
    except Exception:
        # Token already invalid — nothing to blacklist
        pass