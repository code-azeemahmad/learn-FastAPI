from pydantic import BaseModel
from pydantic import Field
from pydantic import EmailStr

# class Address(BaseModel):
#     city: str
#     country: str

class UserCreate(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=30,
        description="user name",
        pattern=r"^[a-zA-Z0-9_]+$"
    )
    email: EmailStr
    password: str
    # address: Address | None = None    # nested models

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr



# Field(...) means Field is required
# Field(default="Ahmad") or stock: int = 0  # default
# hobby: str | None = None    # optional
# description="user name"   # Field meta data
