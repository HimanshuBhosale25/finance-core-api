from typing import Annotated, Generator

import redis as redis_lib
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User, UserRole, UserStatus

bearer_scheme = HTTPBearer()

# ── Database ──────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Redis ─────────────────────────────────────────────────

def get_redis() -> redis_lib.Redis:
    return redis_lib.from_url(settings.REDIS_URL, decode_responses=True)


# ── Current User ──────────────────────────────────────────

def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
    redis: Annotated[redis_lib.Redis, Depends(get_redis)],
) -> User:
    token = credentials.credentials

    # 1. Check blacklist first — fast Redis lookup before any DB hit
    if redis.get(f"blacklist:{token}"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated. Please log in again.",
        )

    # 2. Decode and validate JWT
    try:
        payload = decode_access_token(token)
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise ValueError("Missing subject in token")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Fetch user from DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )

    # 4. Check account is active
    if user.status == UserStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Contact an admin.",
        )

    return user


# ── RBAC ──────────────────────────────────────────────────

def require_roles(*roles: UserRole):
    """
    Factory that returns a dependency enforcing role-based access.

    Usage:
        Depends(require_roles(UserRole.ADMIN))
        Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))
    """
    def checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user

    return checker


# ── Typed shortcuts (used as Depends() in route signatures) ──

DBSession = Annotated[Session, Depends(get_db)]
RedisClient = Annotated[redis_lib.Redis, Depends(get_redis)]
CurrentUser = Annotated[User, Depends(get_current_user)]

AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
AnalystUser = Annotated[User, Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN))]
AnyAuthUser = Annotated[User, Depends(get_current_user)]