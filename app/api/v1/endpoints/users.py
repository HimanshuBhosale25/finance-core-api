from fastapi import APIRouter

from app.core.dependencies import DBSession, AdminUser
from app.schemas.user import UserCreate, UserUpdate, UserStatusUpdate, UserResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
def list_users(db: DBSession, current_user: AdminUser):
    return user_service.get_all_users(db)


@router.post("", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate, db: DBSession, current_user: AdminUser):
    return user_service.create_user(db, payload)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DBSession, current_user: AdminUser):
    return user_service.get_user_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: DBSession, current_user: AdminUser):
    return user_service.update_user(db, user_id, payload)


@router.patch("/{user_id}/status", response_model=UserResponse)
def update_user_status(user_id: int, payload: UserStatusUpdate, db: DBSession, current_user: AdminUser):
    return user_service.update_user_status(db, user_id, payload)


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: DBSession, current_user: AdminUser):
    user_service.delete_user(db, user_id, current_user_id=current_user.id)