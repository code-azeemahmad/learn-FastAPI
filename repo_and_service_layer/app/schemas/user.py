from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )
    email: EmailStr


class UserPatch(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    email: EmailStr | None = None

'''Our route returns a SQLAlchemy object: return user
Not a dictionary.

from_attributes=True tells Pydantic: "Read values from object attributes."
Without it, you'll get validation errors.'''