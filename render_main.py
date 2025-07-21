from flask import Flask, request
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
import os
import logging
from threading import Lock
from src.config import TELEGRAM_TOKEN as TOKEN, logger, BotMeta
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler

# Configuración
app = Flask(__name__)
post_handler = PostHandler()
resume_handler = ResumeHandler()
coingecko_lock = Lock()

def create_app():
    """Factory para inicialización segura"""
    # 1. Configuración de la aplicación
    application = Application.builder().token(TOKEN).build()

    # 2. Registro de comandos
    async def register_commands():
        await application.bot.set_my_commands([
            BotCommand("start", "Inicia el bot"),
            BotCommand("precio", "Consulta precio de cripto"),
            # ... otros comandos ...
        ])

    # 3. Configuración de handlers
    def setup_handlers():
        setup_base_handlers(application)
        
        async def safe_precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
            with coingecko_lock:
                await precio_cripto(update, context)

        application.add_handler(CommandHandler("precio", safe_precio))
        # ... otros handlers ...

    # 4. Inicialización completa
    setup_handlers()
    application.run_async(register_commands())
    
    return application

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
async def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    await application.update_queue.put(update)
    return "OK", 200

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} ✅", 200

# Punto de entrada principal
def main():
    global application
    application = create_app()
    
    if os.getenv('RENDER'):
        # Configuración para Render
        port = int(os.getenv('PORT', 10000))
        webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
        
        async def set_webhook():
            await application.bot.set_webhook(webhook_url)
        
        application.run_async(set_webhook())
        app.run(host='0.0.0.0', port=port)
    else:
        # Modo desarrollo local
        application.run_polling()

if __name__ == '__main__':
    main()
