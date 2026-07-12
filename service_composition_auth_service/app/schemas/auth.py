from pydantic import BaseModel, Field, EmailStr

class RegisterRequest(BaseModel):   #  this schema belongs to auth
    name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=8)





# What happens when a user signs up?
'''Receive Request --> Validate Request --> Check duplicate 
email --> Hash password --> Save user'''
# Which layer owns each step?
'''
| Task            | Layer              |
| --------------- | ------------------ |
| Validate JSON   | FastAPI + Pydantic |
| Check email     | AuthService        |
| Hash password   | Security           |
| Save user       | Repository         |
| Return response | Router             |
'''