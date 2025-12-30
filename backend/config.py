from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = ""
    veo_api_key: str = ""
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/veo3db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # App Config
    debug: bool = True
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    max_video_duration: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
