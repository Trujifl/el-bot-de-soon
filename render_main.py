from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler
)
import os
import logging
import asyncio

# Configuración inicial
app = FastAPI(title="Telegram Bot API")

# Logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')

# Configuración del bot (igual que en tu versión)
def create_application():
    application = Application.builder().token(TOKEN).build()
    
    from src.handlers.base import setup_base_handlers
    from src.handlers.crypto import precio_cripto
    from src.handlers.post import PostHandler
    from src.handlers.resume import ResumeHandler
    
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

application = create_application()

# Webhook para FastAPI
@app.post('/webhook')
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        logger.info("Update procesado")
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno")

# Health Check
@app.get('/')
async def health_check():
    return {
        "status": "active",
        "service": "Telegram Bot",
        "documentation": "/docs"
    }
