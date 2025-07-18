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
        
        print(f"Canal: {self.CHANNEL_ID} | Admins: {self.ADMIN_IDS}")

    async def handle(self, update: Update, context: CallbackContext) -> None:
        if len(update.message.text.split()) == 1:  # Solo escribió /post
            await update.message.reply_text(
                "📢 *Instrucciones para /post:*\n\n"
                "Envía el comando seguido del contenido de tu publicación:\n"
                "Formato recomendado:\n"
                "`/post Título de tu publicación\n"
                "Contenido detallado aquí...\n"
                "#hashtags #opcionales`\n\n"
                "Ejemplo completo:\n"
                "`/post Análisis de mercado\n"
                "Bitcoin muestra tendencia alcista...\n"
                "#BTC #Cripto`",
                parse_mode="Markdown"
            )
            return
        
        user_id = update.effective_user.id
        if user_id not in self.ADMIN_IDS:
            await update.message.reply_text("❌ Solo administradores pueden publicar")
            return
        
        post_text = update.message.text.replace('/post', '', 1).strip()
        self.pending_posts[user_id] = {"text": post_text}
        
        keyboard = [
            [InlineKeyboardButton("✅ Publicar", callback_data=f"confirm_post_{user_id}"),
             InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_post_{user_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✍️ Vista previa del post:\n\n"
            f"{post_text}\n\n"
            "¿Quieres publicarlo en el canal?",
            reply_markup=reply_markup
        )

    async def handle_confirmation(self, update: Update, context: CallbackContext) -> None:
        """Maneja la confirmación solo desde el bot"""
        query = update.callback_query
        await query.answer()
        
        user_id = int(query.data.split('_')[-1])
        
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