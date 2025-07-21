import os
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Configuración básica
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Activo\n\n"
        "Comandos disponibles:\n"
        "/precio [cripto] - Consultar precio\n"
        "/echo [texto] - Repetir texto\n"
        "/help - Ayuda"
    )

async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cripto = context.args[0].lower() if context.args else "bitcoin"
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": cripto,
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            },
            timeout=10
        )
        data = response.json()
        
        if cripto in data:
            await update.message.reply_text(
                f"📊 {cripto.upper()}\n"
                f"Precio: ${data[cripto]['usd']:,.2f}\n"
                f"24h: {data[cripto]['usd_24h_change']:.2f}%"
            )
        else:
            await update.message.reply_text("⚠️ Criptomoneda no encontrada")
    except Exception as e:
        logger.error(f"Error en precio_cripto: {e}")
        await update.message.reply_text("❌ Error al consultar precio")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if text:
        await update.message.reply_text(f"🔹 {text}")
    else:
        await update.message.reply_text("ℹ️ Uso: /echo [texto]")

def setup_application():
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("echo", echo))
    
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: u.message.reply_text("Usa /help para ver comandos")
    ))
    
    return application

async def run_bot():
    application = setup_application()
    PORT = int(os.getenv('PORT', 10000))
    
    try:
        await application.initialize()
        await application.start()
        
        # Configuración webhook mejorada
        await application.updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=os.getenv('WEBHOOK_URL').rstrip('/') + "/webhook",
            secret_token=os.getenv('WEBHOOK_SECRET'),
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
        logger.info(f"✅ Bot escuchando en puerto {PORT}")
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        await application.stop()

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido manualmente")
    except Exception as e:
        logger.error(f"❌ Error no manejado: {e}")
