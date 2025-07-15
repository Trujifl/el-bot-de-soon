from telegram import Update
from telegram import Update
from telegram.ext import CallbackContext
from .base import BaseHandler

class HelpHandler(BaseHandler):
    async def handle(self, update: Update, context: CallbackContext):
        await update.message.reply_text(
            "📌 Ayuda disponible:\n"
            "/start - Inicia el bot\n"
            "/precio - Consulta precios\n"
            "/post - Crea publicaciones"
        )