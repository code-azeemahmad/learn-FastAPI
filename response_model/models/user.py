from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        description="user name",
        pattern=r"^[a-zA-Z0-9_]+$"
    )
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class UserUpdate(BaseModel):
    pass

class UserLogin(BaseModel):
    pass

# fastapi autoo validates before sending response
# Use separate request and response models