from models.user import UserResponse, UserCreate
from fastapi import FastAPI
from fastapi import status

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello home"}


@app.post(
        "/users",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED
    )
def create_user(user: UserCreate):
    saved_user = {
        "id": 1,    # KEY = MODEL FIELD NAME
        "username": user.username,
        "email": user.email,
        "password": user.password,
    }
    return saved_user

'''response model does not contain password:
FastAPI automatically removes password from response'''
