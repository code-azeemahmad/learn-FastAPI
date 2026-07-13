from app.exceptions.base import AppException


class UserNotFoundException(AppException):
    """Raised when a user cannot be found."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User with id {user_id} was not found")


class EmailAlreadyExistsException(AppException):
    """Raised when attempting to create or update a duplicate email."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Email '{email}' already exists")


class InvalidCredentialsError(AppException):
    """Raised when authentication fails."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password.")