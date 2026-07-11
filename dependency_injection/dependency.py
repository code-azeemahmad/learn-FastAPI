from fastapi import Depends

def get_settings():
    return {
        "app_name": "Learn FastAPI",
        "version": "1.0"
    }

# dependency should contain shared resources, not unrelated business logic

def get_age() -> int:
    return 20

def get_name(age = Depends(get_age)) -> dict:
    return {
        "name": "azeem",
        "age": age
    }

def profile(name = Depends(get_name)) -> dict:
    return name
