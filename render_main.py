from fastapi import FastAPI, Request, HTTPException
from telegram.ext import Application
import logging
from src.config import settings, logger

app = FastAPI(
    title="SoonBot API",
    description="API para el bot de Telegram especializado en criptomonedas",
    version="2.0"
)

async def setup_bot():
    """Configuración modular del bot"""
    bot_app = Application.builder().token(settings.TELEGRAM_TOKEN).build()
    
    # Importación diferida para evitar circularidad
    from src.handlers import setup_handlers
    from src.services.openai import generar_respuesta_ia
    
    # Configura handlers existentes
    setup_handlers(bot_app)
    
    # Configuración adicional si es necesaria
    if settings.ALLOWED_CHANNELS:
        from src.handlers.channel import ChannelForwarder
        channel_handler = ChannelForwarder(settings.ALLOWED_CHANNELS)
        bot_app.add_handler(MessageHandler(
            filters.ChatType.CHANNEL,
            channel_handler.forward_to_group
        ))
    
    return bot_app

@app.on_event("startup")
async def on_startup():
    """Inicialización asíncrona"""
    try:
        app.state.bot = await setup_bot()
        await app.state.bot.initialize()
        logger.info("✅ Bot iniciado correctamente")
    except Exception as e:
        logger.critical(f"❌ Error de inicio: {str(e)}")
        raise

@app.post("/webhook")
async def webhook(request: Request):
    """Endpoint para webhooks de Telegram"""
    try:
        data = await request.json()
        update = Update.de_json(data, app.state.bot.bot)
        await app.state.bot.process_update(update)
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Error interno")

@app.get("/")
async def health_check():
    """Endpoint de verificación de estado"""
    return {
        "status": "active",
        "bot": "SoonBot",
        "services": {
            "openai": bool(settings.OPENAI_API_KEY),
            "coingecko": bool(settings.COINGECKO_API_KEY),
            "channels": bool(settings.ALLOWED_CHANNELS)
        }
    }
