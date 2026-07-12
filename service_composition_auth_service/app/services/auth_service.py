from app.core.security import PasswordHasher
from app.exceptions.user import EmailAlreadyExistsException, InvalidCredentialsError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest


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
    

    def login(self, request: LoginRequest) -> User:
        user = self.repository.get_by_email(request.email)

        if not user:
            raise InvalidCredentialsError()

        is_valid = self.password_hasher.verify(
            request.password,
            user.password_hash,
        )

        if not is_valid:
            raise InvalidCredentialsError()

        return user
    
'''AuthService --> UserRepository --> PasswordHasher'''



'''
register()
login()
refresh_token()
change_password()
forgot_password()
reset_password()
logout()
verify_email()
resend_verification_email()
'''