# /core/config.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_TOKEN: str
    ADMIN_IDS: int
    XRAY_CONFIG_PATH: str = "/app/xray/config.json"
    XRAY_CONTAINER: str = "xray"
    AVAILABLE_IPS: List[str] = ["185.170.154.69", "185.170.154.75", "185.170.154.76"]
    TEST_DAYS: int = 1
    PAID_DAYS: int = 30
    DATABASE_PATH: str = "/test-env/vpn.db"
    REALITY_DEST: str = "www.cloudflare.com:443"
    REALITY_SERVER_NAME: str = "www.cloudflare.com"
    MIN_PORT: int = 10000
    MAX_PORT: int = 50000
    XRAY_API_URL: str = "http://127.0.0.1:10086"
    XRAY_PUBLIC_KEY: str = "2IGHoWQM88SBBBOtP5TIZokxwGlUGYV0_Q3qrvoVfhI"
    XRAY_SHORT_ID: str = "02f679de"
    XRAY_SNI: str = "www.cloudflare.com"

   
    class Config:
        env_file = ".env"

settings = Settings()
