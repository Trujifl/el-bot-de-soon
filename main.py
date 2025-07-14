import sys
import os
import asyncio
from threading import Thread
from flask import Flask, jsonify, request
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import BotCommand, Update
from waitress import serve
from src.config import (
    TELEGRAM_TOKEN as TOKEN,
    PORT,
    WEBHOOK_URL,
    RENDER,
    logger,
    BotMeta
)

# Inicialización de Flask
app = Flask(__name__)

# Variable global para la aplicación del bot
application = None

@app.route('/')
def home():
    return jsonify({"status": "running", "bot": BotMeta.NAME}), 200

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    """Endpoint para recibir actualizaciones de Telegram"""
    if request.headers.get('content-type') == 'application/json':
        json_data = await request.get_json()
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
    return '', 200

def run_flask():
    """Inicia el servidor web con Waitress"""
    serve(app, host="0.0.0.0", port=PORT)

async def setup_bot():
    """Configuración completa del bot"""
    global application  # Usamos la variable global
    
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
    
    return application

async def run_bot():
    """Ejecución principal del bot"""
    global application
    
    try:
        application = await setup_bot()
        
        if RENDER:
            logger.info("Configurando webhook...")
            await application.initialize()
            await application.bot.set_webhook(
                url=f"{WEBHOOK_URL}/{TOKEN}",
                secret_token=os.getenv("WEBHOOK_SECRET", "SECRET_TOKEN")
            )
            # Mantener el bot activo
            while True:
                await asyncio.sleep(3600)
        else:
            logger.info("Iniciando en modo polling...")
            await application.run_polling()
            
    except Exception as e:
        logger.error(f"Error en run_bot: {str(e)}")
        raise

def main():
    try:
        if RENDER:
            # Iniciar Flask en segundo plano
            Thread(target=run_flask, daemon=True).start()
            logger.info(f"Servidor web iniciado en puerto {PORT}")
        
        # Configurar e iniciar el bot
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
        
    except KeyboardInterrupt:
        logger.info("Detención solicitada...")
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()