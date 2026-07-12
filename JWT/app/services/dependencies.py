from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

from app.core.security import PasswordHasher
from app.services.auth_service import AuthService


def get_user_repository(db: Session = Depends(get_db),) -> UserRepository:
    return UserRepository(db)


def get_user_service(repository: UserRepository = Depends(get_user_repository),) -> UserService:
    return UserService(repository)

def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()

def get_auth_service(repository: UserRepository = Depends(get_user_repository), password_hasher: PasswordHasher = Depends(get_password_hasher),) -> AuthService:
    return AuthService(repository=repository, password_hasher=password_hasher,)