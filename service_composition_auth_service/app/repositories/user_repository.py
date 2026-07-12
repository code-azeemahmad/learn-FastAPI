from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserPatch, UserUpdate


class UserRepository:
    """Handles all database operations related to User."""

    def __init__(self, db: Session) -> None:
        self.db = db
    

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )
    

    def get_by_id(self, user_id: int) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )
    
    def get_all(self) -> list[User]:
        return self.db.query(User).all()
    

    def create(self, user: UserCreate) -> User:
        new_user = User(
            name=user.name,
            email=user.email,
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user 


    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()   

    def update(
        self,
        user: User,
        user_data: UserUpdate,
    ) -> User:
        user.name = user_data.name
        user.email = user_data.email

        self.db.commit()
        self.db.refresh(user)

        return user
    

    def patch(
        self,
        user: User,
        user_data: UserPatch,
    ) -> User:

        if user_data.name is not None:
            user.name = user_data.name

        if user_data.email is not None:
            user.email = user_data.email

        self.db.commit()
        self.db.refresh(user)

        return user