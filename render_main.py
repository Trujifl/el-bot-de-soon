# render_main.py
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from telegram import BotCommand
import asyncio
import os
import logging
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    logger,
    BotMeta
)
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler

# Configuración inicial
app = Flask(__name__)
post_handler = PostHandler()
resume_handler = ResumeHandler()

# Configura los comandos del bot (para la interfaz de Telegram)
async def set_bot_commands(application):
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("help", "Muestra ayuda"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto en español"),
        BotCommand("resumen_url", "Resume una página web en español")
    ]
    await application.bot.set_my_commands(commands)

# Crea la aplicación de Telegram con todos los handlers
def create_telegram_app():
    application = Application.builder().token(TOKEN).build()
    
    # Handlers desde src/handlers/
    setup_base_handlers(application)
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("post", post_handler.handle))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
    application.add_handler(CallbackQueryHandler(post_handler.handle_confirmation, pattern="^(confirm|cancel)_post_"))
    
    # Comandos visibles en el menú
    application.post_init = set_bot_commands
    
    return application

# Endpoint para webhooks
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        application = create_telegram_app()
        update = Update.de_json(request.json, application.bot)
        asyncio.run(application.process_update(update))
        logger.info(f"[{BotMeta.NAME}] Update procesado correctamente")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return "Error", 500

# Health check para Render
@app.route('/')
def health_check():
    return f"{BotMeta.NAME} está activo ✅", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 10000))