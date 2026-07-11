from fastapi import APIRouter, Depends, status, HTTPException
from app.database.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserPatch

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

@router.get("/", response_model=list[UserResponse],)
def get_users(db: Session = Depends(get_db),):

    return db.query(User).all()

@router.get("/{user_id}", response_model=UserResponse,)
def get_user(user_id: int, db: Session = Depends(get_db),):

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user

@router.put("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK,)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db),) -> UserResponse:

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.name = user_data.name
    user.email = user_data.email

    db.commit()
    db.refresh(user)

    return user


@router.patch("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK,)
def patch_user(user_id: int, user_data: UserPatch, db: Session = Depends(get_db),) -> UserResponse:

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.email is not None:
        user.email = user_data.email

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT,)
def delete_user(user_id: int, db: Session = Depends(get_db),) -> None:

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    return



'''
db.add(user)    # Marks the object to be inserted.
db.commit() # Writes changes to PostgreSQL.
db.refresh(user) # refresh() reloads the object from the database.
'''