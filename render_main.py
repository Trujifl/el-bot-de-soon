from fastapi import FastAPI, Request, HTTPException, Header
from telegram import Update
from telegram.ext import Application
from src.config import settings, logger
import hmac
import hashlib

app = FastAPI(title="SoonBot API")

async def setup_bot():
    """Configuración del bot con seguridad para Render"""
    bot_app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
    
    # Importación diferida de handlers
    from src.handlers import setup_handlers
    setup_handlers(bot_app)
    
    # Configuración específica para Render
    if settings.RENDER:
        await bot_app.bot.set_webhook(
            url=settings.WEBHOOK_URL,
            secret_token=settings.WEBHOOK_SECRET
        )
    
    return bot_app

@app.on_event("startup")
async def startup():
    try:
        app.state.bot = await setup_bot()
        logger.info(f"Bot iniciado en modo {'Render' if settings.RENDER else 'local'}")
    except Exception as e:
        logger.critical(f"Error de inicio: {str(e)}")
        raise

@app.post("/webhook")
async def webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None)
):
    """Endpoint seguro para webhooks"""
    # Verificación de secreto
    if settings.RENDER:
        if not x_telegram_bot_api_secret_token:
            raise HTTPException(403, "Token secreto requerido")
            
        if not hmac.compare_digest(
            x_telegram_bot_api_secret_token,
            settings.WEBHOOK_SECRET
        ):
            raise HTTPException(403, "Token inválido")
    
    try:
        data = await request.json()
        update = Update.de_json(data, app.state.bot.bot)
        await app.state.bot.process_update(update)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error en webhook: {str(e)}")
        raise HTTPException(500, "Error interno")

@app.get("/")
async def health_check():
    return {
        "status": "active",
        "environment": "Render" if settings.RENDER else "local",
        "features": {
            "openai": bool(settings.OPENAI_API_KEY),
            "webhook": settings.RENDER
        }
    }
