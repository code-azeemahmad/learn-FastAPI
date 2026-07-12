from pwdlib import PasswordHash

class PasswordHasher:
    """Handles password hashing and verification."""

    def __init__(self) -> None:
        self._password_hash = PasswordHash.recommended()

    def hash(self, password: str) -> str:
        """Hash a plaintext password."""
        return self._password_hash.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against its hash."""
        return self._password_hash.verify(
            plain_password,
            hashed_password,
        )