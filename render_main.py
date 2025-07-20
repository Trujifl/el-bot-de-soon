from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from src.config import settings, logger
import asyncio

app = FastAPI()

# Desactiva la generación automática de pyproject.toml
import os
os.environ["MATURIN_PEP517_ARGS"] = "--no-build-isolation"

async def create_bot():
    bot = Application.builder().token(settings.TELEGRAM_TOKEN).build()
    
    # Handlers locales para evitar imports circulares
    from src.handlers.base import setup_base_handlers
    setup_base_handlers(bot)
    
    return bot

@app.on_event("startup")
async def startup():
    try:
        app.state.bot = await create_bot()
        if settings.RENDER:
            await app.state.bot.initialize()  # No usamos webhook para simplificar
        logger.info("✅ Bot iniciado")
    except Exception as e:
        logger.critical(f"🚨 Error de inicio: {e}")
        raise

@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, app.state.bot.bot)
        await app.state.bot.process_update(update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"⚠️ Error en webhook: {e}")
        raise HTTPException(500, "Error interno")

@app.get("/")
def health_check():
    return {"status": "active", "mode": "polling" if not settings.RENDER else "webhook"}
