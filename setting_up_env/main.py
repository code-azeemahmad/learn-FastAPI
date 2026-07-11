from fastapi  import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}   # returned a Python dictionary. FastAPI automatically converts it into JSON.


@app.get("/about")
def about():
    return {"page": "About"}


@app.get("/contact")
def contact():
    return {"page": "Contact"}


'''Route Decorator: Whenever someone sends a 
GET request to /, execute the function below'''