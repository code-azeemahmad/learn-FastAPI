from fastapi import APIRouter, Depends, status

from app.schemas.user import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services.dependencies import get_user_service
from app.services.user_service import UserService

from app.services.dependencies import require_owner_or_admin
from app.services.dependencies import get_user_service, require_roles

from app.models.user import User


router = APIRouter(prefix="/users", tags=["User"])

# refactor the routes to such extent that they read like reading English sentences
# Read it like English:
# When someone POSTs to /users, create a user using the UserService.

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, service: UserService = Depends(get_user_service)) -> UserResponse:
    return service.create_user(user_data)


@router.get("/", response_model=list[UserResponse])
def get_users(service: UserService = Depends(get_user_service)) -> list[UserResponse]:
    return service.get_users()


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserResponse:
    return service.get_user(user_id)


@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_data: UserUpdate, service: UserService = Depends(get_user_service)) -> UserResponse:
    return service.update_user(user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_roles("admin")),
):
    return service.delete_user(user_id)


@router.patch("/{user_id}")
def update_user(
    user_id: int,
    request: UserPatch,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_owner_or_admin),
):
    return service.patch_user(user_id, request)