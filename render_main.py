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


app = Flask(__name__)


application = Application.builder().token(TOKEN).build()
post_handler = PostHandler()
resume_handler = ResumeHandler()


webhook_status_cache = "No verificado"

async def update_webhook_status():
    """Actualiza el estado del webhook periódicamente"""
    global webhook_status_cache
    while True:
        try:
            info = await application.bot.get_webhook_info()
            webhook_status_cache = info.url if info.url else "No configurado"
        except Exception as e:
            webhook_status_cache = f"Error: {str(e)}"
        await asyncio.sleep(300) 

def setup_handlers():
    setup_base_handlers(application)
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("post", post_handler.handle))
    application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
    application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
    application.add_handler(CallbackQueryHandler(
        post_handler.handle_confirmation, 
        pattern="^(confirm|cancel)_post_"
    ))

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update = Update.de_json(request.json, application.bot)
        await application.process_update(update)
        logger.info(f"[{BotMeta.NAME}] Mensaje procesado")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} ✅ | Webhook: {webhook_status_cache}", 200

def run_app():
   
    setup_handlers()
    
   
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(update_webhook_status())
    
   
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 10000)))

if __name__ == '__main__':
    run_app()
