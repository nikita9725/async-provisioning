from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = 'sqlite+aiosqlite:///./tasks.db'


settings = Settings()
