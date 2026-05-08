"""
app/core/config.py
Central configuration — all settings loaded from .env
"""

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # IndiaMART
    indiamart_api_key: str
    indiamart_mobile: str

    # 360dialog WhatsApp
    dialog360_api_key: str
    dialog360_waba_id: str
    whatsapp_from_number: str

    # AWS SES
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "ap-southeast-1"
    ses_from_email: str
    ses_from_name: str

    # Exotel
    exotel_api_key: str
    exotel_api_token: str
    exotel_sid: str
    exotel_virtual_number: str
    exotel_caller_id: str

    # Database
    database_url: str

    # App
    lead_min_quantity: int = 300
    poll_interval_seconds: int = 60
    app_env: str = "production"
    log_level: str = "INFO"

    # Dashboard
    dashboard_username: str = "admin"
    dashboard_password: str

    # Company
    company_name: str = "Phoenix Med Tech (M) Sdn Bhd"
    company_phone: str
    company_email: str
    company_website: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
