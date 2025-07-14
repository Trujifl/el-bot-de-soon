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
    BotMeta
)

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "active", "bot": BotMeta.NAME}), 200

def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

async def bot_main():
    """Función principal asíncrona para el bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Configura handlers aquí (importa dentro de la función para evitar circular imports)
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
    
    # Configura comandos
    commands = [
        BotCommand("start", "Inicia el bot"),
        BotCommand("help", "Muestra ayuda"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto en español"),
        BotCommand("resumen_url", "Resume una página web en español")
    ]
    await application.bot.set_my_commands(commands)
    
    if RENDER:
        logger.info("Modo Webhook - Configurando...")
        await application.initialize()
        await application.bot.set_webhook(
            url=f"{WEBHOOK_URL}/{TOKEN}",
            secret_token=os.getenv("WEBHOOK_SECRET", "SECRET_TOKEN")
        )
        await application.start()
    else:
        logger.info("Modo Polling - Iniciando...")
        await application.run_polling()

def main():
    try:
        if RENDER:
            # Inicia Flask en segundo plano
            Thread(target=run_flask, daemon=True).start()
            logger.info(f"Flask corriendo en puerto {PORT}")
        
        # Configuración especial del event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_main())
        
    except Exception as e:
        logger.error(f"ERROR CRÍTICO: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()