import sys
import os
import asyncio
from threading import Thread
from flask import Flask, jsonify
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters
from telegram import BotCommand
from waitress import serve  # Importación para Waitress
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
    return jsonify({"status": "running", "bot": BotMeta.NAME}), 200

def run_flask():
    serve(app, host="0.0.0.0", port=PORT)

async def setup_bot():
    """Configuración completa del bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Importar handlers aquí para evitar circular imports
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
    
    # Configurar comandos del menú
    await application.bot.set_my_commands([
        BotCommand("start", "Inicia el bot"),
        BotCommand("help", "Muestra ayuda"),
        BotCommand("precio", "Consulta precio de cripto"),
        BotCommand("post", "Crea un post para el canal"),
        BotCommand("resumen_texto", "Resume un texto en español"),
        BotCommand("resumen_url", "Resume una página web en español")
    ])
    
    if RENDER:
        logger.info("Configurando webhook...")
        await application.initialize()
        await application.bot.set_webhook(
            url=f"{WEBHOOK_URL}/{TOKEN}",
            secret_token=os.getenv("WEBHOOK_SECRET", "SECRET_TOKEN")
        )
        return application
    
    logger.info("Iniciando en modo polling...")
    return application

async def run_bot():
    """Ejecución principal del bot"""
    application = await setup_bot()
    
    try:
        if RENDER:
            await application.start()
            while True:
                await asyncio.sleep(3600)  # Mantiene el bot activo
        else:
            await application.run_polling()
    except asyncio.CancelledError:
        logger.info("Deteniendo el bot...")
        await application.stop()
        await application.shutdown()

def main():
    try:
        if RENDER:
            # Iniciar Flask con Waitress (producción)
            Thread(target=run_flask, daemon=True).start()
            logger.info(f"Servidor web iniciado en puerto {PORT}")
        
        # Configurar e iniciar el bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(run_bot())
        except KeyboardInterrupt:
            logger.info("Detención solicitada...")
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()