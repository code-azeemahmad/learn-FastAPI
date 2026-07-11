from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello home"}


@app.get("/users/{user_id}")
def user(user_id: int):
    return {"user_id": user_id}


@app.get("/search")
def search(q: str):
    return {"Query": q}


@app.get("/products")
def get_products(category: str, page: int):
    return {
        "category": category,
        "page": page
    }




# {variable_name}, (variable:Python type hint)
# FastAPI converts the Python dictionary into JSON automatically.