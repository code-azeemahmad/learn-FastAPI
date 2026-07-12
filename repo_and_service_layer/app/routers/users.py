from fastapi import APIRouter, Depends, status, HTTPException
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserPatch

router = APIRouter(prefix="/users", tags=["User"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:

    repository = UserRepository(db)

    existing_user = repository.get_by_email(user_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    return repository.create(user_data)

@router.get("/", response_model=list[UserResponse],)
def get_users(db: Session = Depends(get_db),) -> list[UserResponse]:

    repository = UserRepository(db)

    return repository.get_all()

@router.get("/{user_id}", response_model=UserResponse,)
def get_user(user_id: int, db: Session = Depends(get_db),) -> UserResponse:

    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK,)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),) -> UserResponse:

    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return repository.update(user, user_data)


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK,)
def patch_user(user_id: int, user_data: UserPatch, db: Session = Depends(get_db),) -> UserResponse:

    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return repository.patch(user, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,)
def delete_user(user_id: int, db: Session = Depends(get_db),) -> None:

    repository = UserRepository(db)

    user = repository.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    repository.delete(user)

    return