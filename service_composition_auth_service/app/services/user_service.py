from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserPatch, UserUpdate
from app.models.user import User
from app.exceptions.user import EmailAlreadyExistsException, UserNotFoundException


class UserService:
    """Handles business logic related to users."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository


    def create_user(self, user_data: UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(user_data.email)

        if existing_user:
            raise EmailAlreadyExistsException(user_data.email)
        return self.user_repository.create(user_data)
    

    def get_users(self) -> list[User]:
        return self.user_repository.get_all()
    

    def get_user(self, user_id: int) -> User:   # def get_user reuseable in def delete_user and def update_user
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundException(user_id)
        
        return user


    def delete_user(self, user_id: int) -> None:
        # user = self.user_repository.get_by_id(user_id)

        # if user is None:
        #     raise UserNotFoundException(user_id)

        user = self.get_user(user_id)
        
        return self.user_repository.delete(user)
    

    def update_user(self, user_id: int, user_data: UserUpdate,) -> User:
        user = self.get_user(user_id)

        existing_user = self.user_repository.get_by_email(user_data.email)

        if existing_user and existing_user.id != user.id:
            raise EmailAlreadyExistsException(user_data.email)

        return self.user_repository.update(user, user_data)


    def patch_user(self, user_id: int, user_data: UserPatch,) -> User:
        user = self.get_user(user_id)

        if user_data.email is not None:
            existing_user = self.user_repository.get_by_email(user_data.email)

            if existing_user and existing_user.id != user.id:
                raise EmailAlreadyExistsException(user_data.email)

        return self.user_repository.patch(user, user_data)