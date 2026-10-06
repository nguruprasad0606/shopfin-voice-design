from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ShopFin Voice API"
    secret_key: str = "change-this-secret-key"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./shopfin.db"
    frontend_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
