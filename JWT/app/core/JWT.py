from datetime import UTC, datetime, timedelta
from fastapi.security import HTTPBearer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from app.exceptions.user import InvalidCredentialsError
from app.core.config import settings
from app.schemas.auth import TokenPayload

security = HTTPBearer()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# This file will be responsible only for creating and verifying JWTs.
class JWTService:
    """Handles JWT creation and verification."""

    def create_access_token(self, user_id: int) -> str:
        now = datetime.now(UTC)

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        }

        # creates a compact string that you can send to the client. 
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)    


    def verify_access_token(self, token: str) -> TokenPayload:
        """
        Decode and verify a JWT.

        Raises an exception if the token is invalid.
        """

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM],
            )

            return TokenPayload.model_validate(payload) # Pydantic validates the decoded data and returns a TokenPayload instance

        except ExpiredSignatureError:
            raise InvalidCredentialsError()

        except InvalidTokenError:
            raise InvalidCredentialsError()