from pydantic import BaseModel, Field, EmailStr

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


'''
Client

↓

POST /auth/login

↓

AuthService

↓

Verify Password

↓

JWTService

↓

Generate Token

↓

Return Token
'''