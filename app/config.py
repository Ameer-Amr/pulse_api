from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext

class Settings(BaseSettings):
    # These match the names in your .env / docker-compose
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ENVIRONMENT: str
    
    # We build the URL using the service name 'db' from docker-compose
    @property
    def DATABASE_URL(self) -> str:
        if self.POSTGRES_HOST == "db:5432":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}?sslmode=require&channel_binding=require"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
templates = Jinja2Templates(directory="templates")
