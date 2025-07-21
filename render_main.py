import os
import logging
import asyncio
import requests
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)
from openai import OpenAI

# Configuración básica
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración de APIs
COINGECKO_API = "https://api.coingecko.com/api/v3"
OPENAI_CLIENT = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- Handlers Principales ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    await update.message.reply_text(
        "🤖 Bot Cripto-IA Activo\n\n"
        "Comandos disponibles:\n"
        "/precio [cripto] - Consultar precio\n"
        "/resumen [texto] - Resumen con IA\n"
        "/post - Crear publicación\n"
        "/help - Mostrar ayuda"
    )

async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta precios de criptomonedas"""
    try:
        cripto = context.args[0].lower() if context.args else "bitcoin"
        response = requests.get(
            f"{COINGECKO_API}/simple/price",
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
        logger.error(f"Error en precio_cripto: {str(e)}")
        await update.message.reply_text("❌ Error al consultar precio")

async def resumen_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera resumen con OpenAI"""
    try:
        texto = " ".join(context.args)
        if not texto:
            await update.message.reply_text("ℹ️ Uso: /resumen [texto a resumir]")
            return
            
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Resume esto en 3 puntos clave:\n{texto}"
            }],
            max_tokens=150
        )
        
        await update.message.reply_text(
            f"📝 Resumen IA:\n{response.choices[0].message.content}"
        )
    except Exception as e:
        logger.error(f"Error en resumen_ia: {str(e)}")
        await update.message.reply_text("❌ Error al generar resumen")

async def post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la creación de posts"""
    try:
        # Lógica para crear posts
        await update.message.reply_text("✏️ Envía el contenido de tu post:")
        
        # Aquí iría la lógica para guardar el post y confirmar
        # ...
        
    except Exception as e:
        logger.error(f"Error en post_handler: {str(e)}")
        await update.message.reply_text("❌ Error al crear post")

# --- Configuración de la Aplicación ---
def setup_application():
    """Configura todos los handlers"""
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Comandos principales
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("resumen", resumen_ia))
    application.add_handler(CommandHandler("post", post_handler))
    
    # Mensajes no reconocidos
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda u, c: u.message.reply_text("Usa /help para ver comandos")
    ))
    
    return application

# --- Ejecución Principal ---
async def run_bot():
    application = setup_application()
    
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 10000)),
        webhook_url=os.getenv('WEBHOOK_URL'),
        secret_token=os.getenv('WEBHOOK_SECRET'),
        drop_pending_updates=True
    )
    
    logger.info("✅ Bot iniciado correctamente")
    await asyncio.Event().wait()  # Ejecución continua

if __name__ == '__main__':
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Deteniendo el bot...")
    except Exception as e:
        logger.error(f"❌ Error fatal: {str(e)}")
