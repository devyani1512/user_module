from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/dcc_userdb"
    SECRET_KEY: str = "change-this-secret"
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()
