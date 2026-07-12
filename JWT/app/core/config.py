from dotenv import load_dotenv
from pathlib import Path
import os

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


class Settings:
    """Application configuration."""

    def __init__(self) -> None:
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SECRET_KEY = os.getenv("SECRET_KEY")

        if not self.DATABASE_URL:
            raise RuntimeError(
                f"DATABASE_URL not found. Looked for .env at {env_path}"
            )
        
        if not self.SECRET_KEY:
            raise RuntimeError(
                f"SECRET_KEY not found. Looked for .env at {env_path}"
            )


settings = Settings()

'''
DATABASE_URL
SECRET_KEY
REDIS_URL
SMTP_HOST
SMTP_PORT

floating around as globals?

No, Instead

settings.DATABASE_URL
settings.SECRET_KEY
settings.REDIS_URL
'''