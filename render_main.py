from flask import Flask, request, Response
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
import asyncio
import logging
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    OPENAI_API_KEY,
    logger,
    BotMeta
)
from src.services.coingecko import CoinGeckoAPI
from openai import OpenAI
import os

# Configuración Flask
app = Flask(__name__)

# Clients
coingecko = CoinGeckoAPI()
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# Application Builder
def create_application():
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("precio", precio_cripto))
    application.add_handler(CommandHandler("resumen", resumen_ia))
    
    return application

# Global Application Instance
application = create_application()

# ----- Handlers -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔹 {BotMeta.NAME} activo\n"
        "/precio [cripto] - Consultar precios\n"
        "/resumen [texto] - Resumen con IA"
    )

async def precio_cripto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cripto = context.args[0] if context.args else "bitcoin"
    try:
        precio = coingecko.obtener_precio(cripto)
        await update.message.reply_text(
            f"💰 {precio['nombre']} ({precio['simbolo']})\n"
            f"Precio: ${precio['precio']:.2f}\n"
            f"24h: {precio['cambio_24h']:.2f}%"
        )
    except Exception as e:
        await update.message.reply_text("❌ Error obteniendo precio")
        logger.error(f"Error en precio_cripto: {str(e)}")

async def resumen_ia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = " ".join(context.args)
    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"Resume esto en 3 puntos clave:\n{texto}"
            }]
        )
        await update.message.reply_text(
            f"📝 Resumen IA:\n{response.choices[0].message.content}"
        )
    except Exception as e:
        await update.message.reply_text("❌ Error con IA")
        logger.error(f"Error en resumen_ia: {str(e)}")

# ----- Webhook Config -----
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        if not application.running:
            await application.initialize()
            await application.start()
            
        update = Update.de_json(request.get_json(), application.bot)
        await application.process_update(update)
        return "", 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return "Error", 500

@app.route('/')
def health_check():
    return f"{BotMeta.NAME} Webhook ✅", 200

# ----- Startup -----
async def run_webhook():
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.getenv('PORT', 10000)),
        webhook_url=os.getenv('WEBHOOK_URL'),
        secret_token=os.getenv('WEBHOOK_SECRET'),
        drop_pending_updates=True
    )

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.getenv('PORT', 10000)))
    asyncio.run(run_webhook())
