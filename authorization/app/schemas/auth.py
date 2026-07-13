from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class RegisterRequest(BaseModel):   #  this schema belongs to auth
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)
    

class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr
    password: str = Field(...)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    iat: datetime


'''
A JWT is just JSON.
For example:
{
    "sub": "5",
    "iat": 1752300000,
    "exp": 1752301800
}

PyJWT returns: dict[str, Any]
But dictionaries don't provide:

- Type safety
- Validation
- Autocomplete
- Self-documentation

That's why we convert the decoded payload into a Pydantic model.
'''