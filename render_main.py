from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
import os
import logging
import asyncio
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    logger,
    BotMeta
)
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler

# Inicialización Flask
app = Flask(__name__)

# Configuración global del bot
def create_application():
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
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

# Instancia única inicializada
application = create_application()

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        # Ejecuta en un nuevo event loop
        asyncio.run(application.process_update(update))
        logger.info(f"[{BotMeta.NAME}] Mensaje procesado")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return "Error", 500

# Health Check
@app.route('/')
def health_check():
    return f"{BotMeta.NAME} ✅", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))
