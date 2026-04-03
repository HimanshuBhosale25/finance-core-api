from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.dependencies import DBSession, RedisClient, CurrentUser
from app.schemas.auth import LoginRequest, TokenResponse, MeResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service, user_service

router = APIRouter(prefix="/auth", tags=["Auth"])
bearer_scheme = HTTPBearer()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: DBSession):
    return auth_service.register_user(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DBSession):
    token = auth_service.login_user(db=db, payload=payload)
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=200)
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    redis: RedisClient,
):
    auth_service.logout_user(token=credentials.credentials, redis=redis)
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=MeResponse)
def me(current_user: CurrentUser):
    return current_user