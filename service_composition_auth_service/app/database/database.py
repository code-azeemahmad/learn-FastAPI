from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# engine is the bridge between Python and PostgreSQL.
# echo=True, prints generated SQL in the terminal
# Calling yield returns a generator, producing values one at a time.