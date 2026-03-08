from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hashbreaker"

    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    REDIS_URL: str = "redis://localhost:6379/0"

    JOBS_QUEUE: str = "jobs_queue"
    RESULTS_QUEUE: str = "results_queue"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()