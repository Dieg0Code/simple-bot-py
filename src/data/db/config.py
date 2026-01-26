from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "simple_bot_db"
    db_user: str = "simple_bot_user"
    db_password: str
    db_timezone: str = "America/Santiago"
    google_api_key: str

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?options=-c%20timezone%3D{self.db_timezone}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
