from fastapi import APIRouter, Depends, status
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User

router = APIRouter(prefix="/users", tags=["User"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(db: Session = Depends(get_db)):
    user = User(
        name="Azeem",
        email="azeem@example.com",
    )

    db.add(user)
    db.commit() 
    db.refresh(user)

    return user


@router.get("/")
def get_users(
    db: Session = Depends(get_db),
):
    users = db.query(User).all()

    return users


'''
db.add(user)    # Marks the object to be inserted.
db.commit() # Writes changes to PostgreSQL.
db.refresh(user) # refresh() reloads the object from the database.
'''