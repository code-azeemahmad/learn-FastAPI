from models.user import UserResponse, UserCreate
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello home"}


@app.post("/users")
def create_user(user: UserCreate):
    return {
        "message": "user created successfully",
        "user": user
    }

