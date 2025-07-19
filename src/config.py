# src/config.py
from pydantic import BaseSettings, Field, validator
from typing import List
import logging
import os

class Settings(BaseSettings):
    # --- Configuración Requerida ---
    TELEGRAM_TOKEN: str = Field(..., env="TELEGRAM_TOKEN")
    TELEGRAM_ADMIN_IDS: List[int] = Field(..., env="TELEGRAM_ADMIN_IDS")
    TELEGRAM_CHANNEL_ID: str = Field(..., env="TELEGRAM_CHANNEL_ID")
    
    # --- Configuración Render ---
    PORT: int = Field(10000, env="PORT")
    WEBHOOK_URL: str = Field(..., env="WEBHOOK_URL")
    WEBHOOK_SECRET: str = Field(..., env="WEBHOOK_SECRET")
    RENDER: bool = Field(False, env="RENDER")
    
    # --- OpenAI (Opcional) ---
    OPENAI_API_KEY: str = Field("", env="OPENAI_API_KEY")
    
    # Validación para ADMIN_IDS
    @validator('TELEGRAM_ADMIN_IDS', pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(id.strip()) for id in v.split(',') if id.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Configuración del logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Carga de configuración
settings = Settings()

# Validación adicional
if not settings.TELEGRAM_TOKEN:
    logger.critical("TELEGRAM_TOKEN no configurado")
    raise ValueError("Token de Telegram requerido")

if settings.RENDER and not settings.WEBHOOK_URL:
    logger.warning("WEBHOOK_URL no configurado en entorno de Render")
