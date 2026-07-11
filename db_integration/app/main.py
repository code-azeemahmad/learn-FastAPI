from fastapi import FastAPI

from app.database.base import Base
from app.database.database import engine

# Import models so SQLAlchemy registers them
from app.models import user  # noqa: F401

app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    

'''from app.models import user
ensures the User model is registered with SQLAlchemy 
before create_all() runs'''