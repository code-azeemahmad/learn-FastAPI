from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["Users"]  # Use tags to organize Swagger documentation.
)

users = ["Ali", "Sara", "Ahmed"]

@router.get("/")
def get_users():
    return {
        "users": users
    }

@router.get("/{user_id}")
def get_user(user_id: int):
    return {
        "user_id": users[user_id]
    }

