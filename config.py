import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Telegram Bot Token
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Yuklab olingan fayllar saqlanadigan vaqtinchalik papka
    DOWNLOAD_DIR: str = "downloads"

settings = Settings()

# Yuklab olish papkasi mavjud bo'lmasa yaratamiz
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)

