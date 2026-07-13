from fastapi import APIRouter, Depends, status

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.dependencies import get_auth_service
from app.models.user import User
from app.services.dependencies import get_current_user, get_user_service, require_roles
from app.services.user_service import UserService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(request: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> UserResponse:
    return service.register(request)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.login(request)


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_roles("admin")),
):
    return service.delete_user(user_id)