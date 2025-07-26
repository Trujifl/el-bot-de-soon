from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.config import logger

class PostHandler:
    CHANNEL_ID = -1002348706229  
    TOPIC_ID = 8223              

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if not message:
            return

        await message.reply_text(
            f"🧪 chat_id: `{update.effective_chat.id}`\n"
            f"🧪 thread_id: `{message.message_thread_id}`",
            parse_mode="Markdown"
        )

        context.user_data["pending_post"] = message.text

        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data="confirm_post_"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_post_"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message.reply_text(
            "¿Quieres publicar este mensaje en el canal?",
            reply_markup=reply_markup
        )

    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_post_":
            content = context.user_data.get("pending_post", "")
            if self.CHANNEL_ID and content:
                try:
                    await context.bot.send_message(
                        chat_id=self.CHANNEL_ID,
                        message_thread_id=self.TOPIC_ID,  
                        text=content
                    )
                    await query.edit_message_text("✅ Post publicado correctamente.")
                except Exception as e:
                    logger.error(f"Error al publicar en el canal: {e}")
                    await query.edit_message_text("❌ Error al publicar en el canal.")
            else:
                await query.edit_message_text("❌ No se pudo recuperar el mensaje original.")

        elif query.data == "cancel_post_":
            await query.edit_message_text("❌ Post cancelado.")

