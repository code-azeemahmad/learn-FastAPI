from fastapi import APIRouter, Depends, status, HTTPException
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["User"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):

    # Convert Pydantic → SQLAlchemy, convert the validated API data into a database object
    user = User(
    name=user_data.name,
    email=user_data.email,
    )

    db.add(user)
    db.commit() 
    db.refresh(user)

    return user # FastAPI converts the SQLAlchemy object into: UserResponse, automatically





'''
db.add(user)    # Marks the object to be inserted.
db.commit() # Writes changes to PostgreSQL.
db.refresh(user) # refresh() reloads the object from the database.
'''