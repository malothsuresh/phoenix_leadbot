"""
app/core/config.py
Central configuration — all settings loaded from .env
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # IndiaMART
    indiamart_api_key: str = ""
    indiamart_mobile: str = "NA"

    # 360dialog WhatsApp
    dialog360_api_key: str = ""
    dialog360_waba_id: str = ""
    whatsapp_from_number: str = ""

    # AWS SES
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "ap-southeast-1"
    ses_from_email: str = ""
    ses_from_name: str = "Phoenix Med Tech"

    # Exotel
    exotel_api_key: str = ""
    exotel_api_token: str = ""
    exotel_sid: str = ""
    exotel_virtual_number: str = ""
    exotel_caller_id: str = ""

    # Database
    database_url: str = "sqlite:///./phoenix_leadbot.db"

    # App
    lead_min_quantity: int = 300
    poll_interval_seconds: int = 1800
    app_env: str = "development"
    log_level: str = "INFO"

    # Vercel / runtime control
    enable_poller: bool = False
    dry_run: bool = True

    # Dashboard
    dashboard_username: str = "admin"
    dashboard_password: str = "change_this_password"

    # Company
    company_name: str = "Phoenix Med Tech (M) Sdn Bhd"
    company_phone: str = "+60123456789"
    company_email: str = "sales@phoenixmedtech.com"
    company_website: str = "https://www.phoenixmedtech.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()