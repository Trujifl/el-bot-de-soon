from telegram import Update
from telegram.ext import CallbackContext
from src.handlers.base import BaseHandler

class HelpHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext) -> None:
        """Muestra la ayuda."""
        help_text = """
        📌 *Comandos disponibles*:
        - /post - Crea un post para el canal.
        - /resumen_texto - Resume un texto (traduce al español).
        - /resumen_url - Resume una página web (traduce al español).
        - /help - Muestra esta ayuda.
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")