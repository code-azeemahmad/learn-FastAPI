from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserPatch, UserUpdate
from app.models.user import User
from fastapi import HTTPException, status


class UserService:
    """Handles business logic related to users."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository


    def create_user(self, user_data: UserCreate) -> User:
        existing_user = self.repository.get_by_email(user_data.email)

        if existing_user:
            raise  HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        return self.repository.create(user_data)
    

    def get_users(self) -> list[User]:
        return self.repository.get_all()
    

    def get_user(self, user_id: int) -> User:   # def get_user reuseable in def delete_user and def update_user
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user


    def delete_user(self, user_id: int) -> None:
        # user = self.repository.get_by_id(user_id)

        # if user is None:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="User not found"
        #     )

        user = self.get_user(user_id)
        
        return self.repository.delete(user)
    

    def update_user(self, user_id: int, user_data: UserUpdate,) -> User:
        user = self.get_user(user_id)

        existing_user = self.repository.get_by_email(user_data.email)

        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        return self.repository.update(user, user_data)


    def patch_user(self, user_id: int, user_data: UserPatch,) -> User:
        user = self.get_user(user_id)

        if user_data.email is not None:
            existing_user = self.repository.get_by_email(user_data.email)

            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists",
                )

        return self.repository.patch(user, user_data)