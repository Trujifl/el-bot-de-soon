from telegram.ext import CommandHandler, MessageHandler, filters
from .base import start, help_command, mensaje_generico, unknown_command, BaseHandler
from .crypto import precio_cripto
from .post import PostHandler
from .resume import ResumeHandler
from .help import HelpHandler  



def setup_handlers(application):
    """
    Configura todos los handlers en el orden CORRECTO
    Versión corregida con todas las importaciones necesarias
    """
    # 1. Handler para mensajes NO comandos (PRIMERO)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mensaje_generico
        )
    )
    
    
    # 2. Handlers de comandos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_generico))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("precio", precio_cripto))
    
    
    # 3. Handler para comandos desconocidos
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
handlers = [
    PostHandler(),
    ResumeHandler()
]