import os
import logging
import random
from pathlib import Path
from telegram.ext import Application  # Importación añadida

def initialize_bot():
    """Inicializa y configura la aplicación de Telegram"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN no está configurado")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.initialize()  # Inicialización explícita
    return application

# Configuración de logging mejorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot_errors.log', encoding='utf-8')  # Añadido encoding
    ]
)
logger = logging.getLogger(__name__)

# Carga de variables de entorno más robusta
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path, override=True)  # Añadido override

# Configuración esencial con validación
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id.strip()]
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip() or None  # Mejor manejo de valores vacíos

# Clases de configuración mejoradas
class BotMeta:
    NAME = "SoonBot"
    VERSION = "2.0"
    EMOJI = "🚀"
    DESCRIPTION = "Asistente de criptomonedas"
    
    @classmethod
    def full_name(cls):
        return f"{cls.NAME} {cls.EMOJI} v{cls.VERSION}"

class BotPersonality:
    TONO = "Profesional pero cercano"
    CRIPTOS_COMUNES = ["bitcoin", "ethereum", "binancecoin", "solana"]
    
    PERSONALIDAD_IA = {
        "role": "system",
        "content": (
            "Eres SoonBot, un asistente especializado en criptomonedas. "
            "Tono: profesional pero cercano. "
            "Conocimientos: blockchain, trading, tecnología. "
            "Estilo: conciso pero informativo. "
            "Emojis: 🚀 (oportunidades), ⚠️ (riesgos). "
            "Precios: siempre mencionar fuente (CoinGecko). "
            "Preguntas técnicas: incluir ejemplos prácticos."
        )
    }
    
    @classmethod
    def get_ia_prompt(cls, user_message: str, username: str) -> list:
        return [
            cls.PERSONALIDAD_IA,
            {
                "role": "user",
                "content": f"{username} pregunta: {user_message}"
            }
        ]
    
    @classmethod
    def get_random_saludo(cls, nombre: str) -> str:
        saludos = [
            f"¡Hola {nombre}! ¿En qué puedo ayudarte hoy?",
            f"¡Buenos días {nombre}! Listo para operar 🚀",
            f"¡{nombre}! ¿Qué cripto analizamos hoy? 📊"
        ]
        return random.choice(saludos)

class APIConfig:
    COINGECKO_URL = "https://api.coingecko.com/api/v3"
    COINGECKO_TIMEOUT = 30
    REQUEST_HEADERS = {
        "User-Agent": "SoonBot/2.0 (+https://github.com/tu-repositorio)",
        "Accept": "application/json"
    }
    
    @classmethod
    def get_coingecko_headers(cls):
        return cls.REQUEST_HEADERS.copy()
