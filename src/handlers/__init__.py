from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from .base import start, help_command, handle_message
from .crypto import precio_cripto
from .post import PostHandler
from .resume import ResumeHandler

def setup_handlers(app):
    # Handlers básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("precio", precio_cripto))
    
    # Handler para mensajes
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # Handlers de Post
    post_handler = PostHandler()
    app.add_handler(CommandHandler("post", post_handler.handle))
    app.add_handler(CallbackQueryHandler(
        post_handler.handle_confirmation,
        pattern="^(confirm|cancel)_post_"
    ))
    
    # Handlers de Resume
    resume_handler = ResumeHandler()
    app.add_handler(CommandHandler("resumen_texto", resume_handler.handle_resumen_texto))
    app.add_handler(CommandHandler("resumen_url", resume_handler.handle_resumen_url))