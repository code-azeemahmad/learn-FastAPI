from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=True,  # temporary nullable=True for two phase migration
    )


'''password_hash: Mapped[str] = mapped_column(nullable=True)
Learn about two phase migration and back fill hashes'''

# expand and contract migration