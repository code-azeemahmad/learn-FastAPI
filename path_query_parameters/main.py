from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "hello home"}


# @app.get("/users/{user_id}")
# def user(user_id: int) -> dict:
#     return {"user_id": user_id}


@app.get("/search")
def search(q: str):
    return {"Query": q}


@app.get("/products")
def get_products(category: str, page: int):
    return {
        "category": category,
        "page": page
    }

# @app.get("/option")
# def option(q: str | None = None):   # optional query parameter
#     return {"query": q}

@app.get("/option")
def option(q: str = "option"):   # default query parameter
    return {"query": q}


# mixing path and query parameters
@app.get("/users/{user_id}")
def get_user(user_id: int, details: bool = False):
    return {"user_id": user_id, "details": details}

# {variable_name}, (variable:Python type hint)
# FastAPI converts the Python dictionary into JSON automatically.

# FastAPI expects each combination of HTTP method + path to be unique.