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

# Logger inicial
logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class BotMeta:
    NAME = "MiBot"

# Carga de variables (sin circularidad)
TOKEN = os.getenv('TELEGRAM_TOKEN')

def create_application():
    """Factory para la aplicación del bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Importación local para evitar circularidad
    from src.handlers.base import setup_base_handlers
    from src.handlers.crypto import precio_cripto
    from src.handlers.post import PostHandler
    from src.handlers.resume import ResumeHandler
    
    # Configuración de handlers
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
    
    return application

# Instancia del bot
application = create_application()

# Webhook para Render
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        asyncio.run(application.process_update(update))
        logger.info(f"[{BotMeta.NAME}] Update procesado")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {str(e)}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} ✅ | Webhook activo", 200

# Punto de entrada para Render
def create_app():
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
