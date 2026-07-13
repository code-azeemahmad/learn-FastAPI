from fastapi import FastAPI

from app.database.base import Base
from app.database.database import engine
from app.handlers.exception_handlers import register_exception_handlers

from app.middleware.timing import process_time_middleware
from app.routers import users, auth

# Import models so SQLAlchemy registers them
from app.models import user  # noqa: F401

app = FastAPI()

app.middleware("http")(process_time_middleware)

register_exception_handlers(app)
app.include_router(users.router)
app.include_router(auth.router)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)



'''from app.models import user
ensures the User model is registered with SQLAlchemy 
before create_all() runs'''