from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./dcc_userdb.db"    
    SECRET_KEY: str = "change-this-secret"
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()
