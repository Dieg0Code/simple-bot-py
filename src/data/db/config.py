from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "simple_bot_db"
    db_user: str = "simple_bot_user"
    db_password: str
    gemini_api_key: str
    
    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()