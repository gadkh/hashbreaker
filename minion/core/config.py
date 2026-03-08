import os
import socket
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    JOBS_QUEUE: str = "jobs_queue"
    RESULTS_QUEUE: str = "results_queue"
    MINION_ID: str = os.getenv("HOSTNAME", socket.gethostname())
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
settings = Settings()