from dependency import get_settings, profile
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/")
def home(settings = Depends(get_settings)): # It does not call the function immediately
    return settings

@app.get("/settings")
def home(settings = Depends(get_settings)):
    return settings

@app.get("/profile")
def home(settings = Depends(profile)):
    return settings


'''settings = Depends(get_settings)
Before executing this route, call get_settings() and pass its return value into settings.'''