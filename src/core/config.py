from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KubikVision"
    
    # Redis
    REDIS_URL: str
    
    # MinIO (S3)
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str

    # Читаем из .env, но системные переменные имеют приоритет
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()