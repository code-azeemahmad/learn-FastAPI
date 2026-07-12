from fastapi import APIRouter, Depends, status

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(request: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> UserResponse:
    return service.register(request)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    return service.login(request)