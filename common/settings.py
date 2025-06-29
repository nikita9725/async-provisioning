from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./tasks.db"
    rmq_url: str = ""
    rmq_prefetch_count: int = 10
    rmq_taks_routing_key: str = "provisioning_tasks"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


settings = Settings()
