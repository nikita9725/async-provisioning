from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str
    rmq_url: str
    provisioning_service_url: str
    rmq_prefetch_count: int = 10
    rmq_taks_routing_key: str = "provisioning_tasks"
    refresh_status_timeout: int = 10 * 60  # 10 мин
    read_timeout: int = 70  # 70 секунд

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


settings = Settings()
