import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class PostHandler:
    def __init__(self):
        self.pending_posts = {}
        self.CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
        self.ADMIN_IDS = [int(id.strip()) for id in os.getenv("TELEGRAM_ADMIN_IDS", "").split(",") if id.strip()]
        
        print(f"Canal: {self.CHANNEL_ID} | Admins: {self.ADMIN_IDS}")  # Debug

    async def handle(self, update: Update, context: CallbackContext) -> None:
        """Maneja /post solo para admins"""
        user_id = update.effective_user.id
        
        # Verificación de admin
        if user_id not in self.ADMIN_IDS:
            await update.message.reply_text("❌ Solo administradores pueden usar este comando")
            return

        user_input = update.message.text.replace('/post', '').strip()
        if not user_input:
            await update.message.reply_text("Escribe el contenido después de /post")
            return

        # Guarda en pending_posts con confirmación requerida
        self.pending_posts[user_id] = {"text": user_input}
        
        keyboard = [
            [InlineKeyboardButton("✅ Publicar", callback_data=f"confirm_post_{user_id}"),
             InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_post_{user_id}")]
        ]
        
        await update.message.reply_text(
            f"✍️ Post pendiente:\n\n{user_input}\n\n¿Publicar en el canal?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_confirmation(self, update: Update, context: CallbackContext) -> None:
        """Maneja la confirmación solo desde el bot"""
        query = update.callback_query
        await query.answer()
        
        user_id = int(query.data.split('_')[-1])
        
        # Doble verificación de admin (seguridad extra)
        if user_id not in self.ADMIN_IDS:
            await query.edit_message_text("❌ Acceso no autorizado")
            return

        if query.data.startswith("confirm_post"):
            post_data = self.pending_posts.get(user_id)
            if post_data:
                try:
                    await context.bot.send_message(
                        chat_id=self.CHANNEL_ID,
                        text=post_data["text"]
                    )
                    await query.edit_message_text("✅ Publicado en el canal")
                except Exception as e:
                    await query.edit_message_text(f"❌ Error: {str(e)}")
                finally:
                    self.pending_posts.pop(user_id, None)
        else:
            await query.edit_message_text("❌ Publicación cancelada")
            self.pending_posts.pop(user_id, None)