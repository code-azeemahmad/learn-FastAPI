from fastapi import Depends, security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

from app.core.security import PasswordHasher
from app.services.auth_service import AuthService
from app.core.JWT import JWTService

from app.models.user import User
from app.exceptions.user import InvalidCredentialsError

security = HTTPBearer()

def get_user_repository(db: Session = Depends(get_db),) -> UserRepository:
    return UserRepository(db)


def get_user_service(repository: UserRepository = Depends(get_user_repository),) -> UserService:
    return UserService(repository)


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_service() -> JWTService:
    return JWTService()


def get_auth_service(
    repository: UserRepository = Depends(get_user_repository), 
    password_hasher: PasswordHasher = Depends(get_password_hasher), 
    jwt_service: JWTService = Depends(get_jwt_service),
    ) -> AuthService:
    return AuthService(repository=repository, password_hasher=password_hasher, jwt_service=jwt_service)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service),
    repository: UserRepository = Depends(get_user_repository),
) -> User:

    payload = jwt_service.verify_access_token(
        credentials.credentials
    )

    user_id = int(payload["sub"])

    user = repository.get_by_id(user_id)

    if user is None:
        raise InvalidCredentialsError()

    return user