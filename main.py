import sys
import os
import asyncio
from threading import Thread
from flask import Flask, jsonify
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import BotCommand
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    PORT,
    WEBHOOK_URL,
    RENDER,
    logger,
    BotMeta,
    BotPersonality
)
from src.handlers.base import setup_base_handlers
from src.handlers.crypto import precio_cripto
from src.handlers.post import PostHandler
from src.handlers.resume import ResumeHandler

# Inicialización de Flask
app = Flask(__name__)

# Endpoint básico para verificar que el bot está en línea
@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "bot": BotMeta.NAME,
        "version": BotMeta.VERSION,
        "mode": "webhook" if RENDER else "polling"
    }), 200

# Configuración de comandos del bot
async def set_bot_commands(application):
    """Configura los comandos visibles en la interfaz de Telegram"""
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("help", "Muestra ayuda"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto en español"),
        BotCommand("resumen_url", "Resume una página web en español")
    ]
    await application.bot.set_my_commands(commands)

# Función para ejecutar el bot
async def run_bot():
    try:
        # 1. Inicialización del bot
        application = Application.builder().token(TOKEN).build()
        
        # 2. Configuración de handlers
        setup_base_handlers(application)
        
        # Handlers específicos
        post_handler = PostHandler()
        resume_handler = ResumeHandler()
        
        application.add_handler(CommandHandler("precio", precio_cripto))
        application.add_handler(CommandHandler("post", post_handler.handle))
        application.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
        application.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))
        application.add_handler(CallbackQueryHandler(
            post_handler.handle_confirmation, 
            pattern="^(confirm|cancel)_post_"
        ))
        
        # 3. Configurar comandos visibles
        await set_bot_commands(application)
        
        logger.info(f"[{BotMeta.NAME} v{BotMeta.VERSION} iniciando...]")
        
        # 4. Modo de ejecución
        if RENDER:
            logger.info("Modo Render - Configurando webhook...")
            await application.bot.set_webhook(
                url=f"{WEBHOOK_URL}/{TOKEN}",
                secret_token=os.getenv("WEBHOOK_SECRET", "SECRET_TOKEN")
            )
            await application.run_polling()  # Mantiene el bot activo
        else:
            logger.info("Modo local - Usando polling...")
            await application.run_polling()
            
    except Exception as e:
        logger.error(f"Error en el bot: {e}")
        raise

# Función para ejecutar Flask
def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

# Punto de entrada principal
def main():
    try:
        if RENDER:
            # Inicia Flask en un hilo separado para Render
            flask_thread = Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()
            
            logger.info(f"Servidor Flask iniciado en puerto {PORT}")
        
        # Inicia el bot en el hilo principal
        asyncio.run(run_bot())
        
    except Exception as e:
        logger.error(f"Error fatal al iniciar: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()