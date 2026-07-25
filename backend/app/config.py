from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ai_dev_platform"

    github_client_id: str = ""
    github_client_secret: str = ""
    github_oauth_redirect_uri: str = "http://localhost:8000/auth/github/callback"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 zile

    frontend_url: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()