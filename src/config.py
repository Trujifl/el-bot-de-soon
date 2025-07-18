import os
from dotenv import load_dotenv
import logging

# Carga variables de entorno
load_dotenv()

class BotMeta:
    NAME = "NombreDeTuBot"
    VERSION = "1.0.0"
    AUTHOR = "TuNombre"

# Configuración esencial (sin dependencias)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 10000))
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-123")

# Configuración de logging
def setup_logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logger

logger = setup_logger()

# Configuración de base de datos (ejemplo)
DATABASE_CONFIG = {
    'uri': os.getenv("DATABASE_URL", "sqlite:///database.db"),
    'connect_args': {'check_same_thread': False} if "sqlite" in os.getenv("DATABASE_URL", "") else {}
}
