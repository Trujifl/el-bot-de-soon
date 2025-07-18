import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler
)

# Configuración básica
app = Flask(__name__)

# Configuración del logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotMeta:
    NAME = "MiBot"
    VERSION = "1.0.0"

# Validación de variables críticas
TOKEN = os.getenv('TELEGRAM_TOKEN')
if not TOKEN:
    logger.error("Falta la variable de entorno TELEGRAM_TOKEN")
    raise ValueError("TELEGRAM_TOKEN no está configurado")

def create_application():
    """Factory para la aplicación del bot con manejo de errores"""
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Importación diferida para evitar circularidad
        from src.handlers.base import setup_base_handlers
        from src.handlers.crypto import precio_cripto
        from src.handlers.post import PostHandler
        from src.handlers.resume import ResumeHandler
        
        # Configuración de handlers con manejo de errores
        try:
            post_handler = PostHandler()
            resume_handler = ResumeHandler()
            
            setup_base_handlers(application)
            application.add_handler(CommandHandler("precio", precio_cripto))
            application.add_handler(CommandHandler("post", post_handler.handle))
            application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
            application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
            application.add_handler(CallbackQueryHandler(
                post_handler.handle_confirmation,
                pattern="^(confirm|cancel)_post_"
            ))
            
            logger.info("Handlers configurados correctamente")
            return application
            
        except Exception as handler_error:
            logger.error(f"Error configurando handlers: {handler_error}")
            raise
            
    except Exception as app_error:
        logger.error(f"Error creando aplicación: {app_error}")
        raise

# Instancia del bot con manejo de errores
try:
    application = create_application()
except Exception as e:
    logger.critical(f"No se pudo iniciar el bot: {e}")
    raise

# Webhook optimizado para Render
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        # Manejo asíncrono mejorado
        async def process_update_async():
            await application.process_update(update)
        
        asyncio.run(process_update_async())
        logger.info(f"[{BotMeta.NAME}] Mensaje procesado: {update.update_id}")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {str(e)}", exc_info=True)
        return "Error", 500

# Health check mejorado
@app.route('/')
def health_check():
    return {
        "status": "healthy",
        "bot": BotMeta.NAME,
        "version": BotMeta.VERSION,
        "webhook": "active"
    }, 200

# Factory para Gunicorn
def create_app():
    """Punto de entrada para WSGI"""
    return app

if __name__ == '__main__':
    # Solo para desarrollo local
    port = int(os.getenv('PORT', 10000))
    logger.info(f"Iniciando en modo desarrollo en puerto {port}")
    app.run(host='0.0.0.0', port=port)
