from app.core.security import PasswordHasher
from app.exceptions.user import EmailAlreadyExistsException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    """Handles authentication-related business logic."""

    def __init__(self, repository: UserRepository, password_hasher: PasswordHasher,) -> None:
        
        self.repository = repository
        self.password_hasher = password_hasher

    def register(self, request: RegisterRequest,) -> User:
        """
        Register a new user.

        Steps:
        1. Check if the email already exists.
        2. Hash the password.
        3. Save the user.
        4. Return the created user.
        """

        existing_user = self.repository.get_by_email(request.email)

        if existing_user:
            raise EmailAlreadyExistsException()

        hashed_password = self.password_hasher.hash(request.password)

        return self.repository.create(name=request.name, email=request.email, password_hash=hashed_password,)
    
'''AuthService --> UserRepository --> PasswordHasher'''