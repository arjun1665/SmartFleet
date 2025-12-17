from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    app_name: str = "predictive-maintenance-platform"
    environment: str = "dev"

    postgres_dsn: str = "postgresql+asyncpg://app:app@postgres:5432/app"
    redis_url: str = "redis://redis:6379/0"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"

    model_path: str = "./artifacts/xgb_model.json"
    encoder_path: str = "./artifacts/feature_encoder.joblib"


settings = Settings()
