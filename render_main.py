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
from openai import OpenAI  # Solo si usas OpenAI (puedes eliminarlo si no)

# Configuración básica
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Handlers Principales (modificados para ser gratuitos) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    await update.message.reply_text(
        "🤖 Bot Gratuito Activo\n\n"
        "Comandos disponibles:\n"
        "/precio [cripto] - Consultar precio (ej: /precio bitcoin)\n"
        "/echo [texto] - Repite tu texto\n"
        "/help - Mostrar ayuda"
    )

async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta precios de criptomonedas (usando CoinGecko API gratuita)"""
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
            await update.message.reply_text("⚠️ Criptomoneda no encontrada. Ejemplo: /precio bitcoin")
    except Exception as e:
        logger.error(f"Error en precio_cripto: {str(e)}")
        await update.message.reply_text("❌ Error al consultar. Intenta más tarde.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Repite el texto del usuario (gratuito)"""
    text = ' '.join(context.args)
    if text:
        await update.message.reply_text(f"🔹 {text}")
    else:
        await update.message.reply_text("ℹ️ Uso: /echo [texto]")

# --- Configuración de la Aplicación ---
def setup_application():
    """Configura la aplicación con handlers gratuitos"""
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("echo", echo))
    
    # Mensajes no reconocidos
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: u.message.reply_text("Usa /help para ver comandos")
    ))
    
    return application

# --- Ejecución Principal (modificada para Render) ---
async def run_bot():
    application = setup_application()
    PORT = int(os.getenv('PORT', 10000))  # Render usa el puerto 10000 por defecto
    
    try:
        await application.initialize()
        await application.start()
        
        # Configuración CRÍTICA para Render:
        await application.updater.start_webhook(
            listen="0.0.0.0",  # Escucha en todas las interfaces
            port=PORT,
            webhook_url=os.getenv('WEBHOOK_URL') + "/webhook",  # ¡Obligatorio!
            secret_token=os.getenv('WEBHOOK_SECRET'),
            drop_pending_updates=True
        )
        
        logger.info(f"✅ Bot activo en puerto {PORT} (Webhook: {os.getenv('WEBHOOK_URL')}/webhook)")
        await asyncio.Event().wait()  # Mantiene el bot en ejecución
        
    except Exception as e:
        logger.error(f"❌ Error fatal: {str(e)}")
    finally:
        await application.stop()

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Bot detenido manualmente")
    except Exception as e:
        logger.error(f"❌ Error no manejado: {str(e)}")
