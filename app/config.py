from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # These match the names in your .env / docker-compose
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # We build the URL using the service name 'db' from docker-compose
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:5432/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
