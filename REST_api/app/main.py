from fastapi import FastAPI
from routers import notes

app = FastAPI()

app.include_router(notes.router)

