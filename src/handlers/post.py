from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.config import logger

class PostHandler:
    CHANNEL_ID = -1002348706229  # Canal de destino
    TOPIC_ID = 8222              # Topic ID dentro del canal

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message
        if not message:
            return

        content = message.text.replace("/post", "").strip()

        if not content:
            await update.message.reply_text(
                "📢 *Instrucciones para /post:*\n"
                "Envía el comando seguido del contenido de tu publicación:\n"
                "\n*Formato recomendado:*\n"
                "/post Título de tu publicación\nContenido detallado aquí...\n#hashtags #opcionales\n"
                "\n*Ejemplo completo:*\n/post Análisis de mercado\nBitcoin muestra tendencia alcista...\n#BTC #Cripto",
                parse_mode="Markdown"
            )
            return

        try:
            title, body = content.split("\n", 1)
        except ValueError:
            title = content
            body = ""

        hashtags = self._generate_hashtags(title + " " + body)
        full_post = f"*{title.strip()}*\n{body.strip()}\n\n{hashtags}" if hashtags else f"*{title.strip()}*\n{body.strip()}"

        preview_text = f"📢 *Vista Previa del Post:*\n\n*{title.strip()}*\n{body.strip()}"
        if hashtags:
            preview_text += f"\n\n_{hashtags}_"

        context.user_data["pending_post"] = {
            "title": title.strip(),
            "body": body.strip(),
            "full": full_post
        }

        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar", callback_data="confirm_post_"),
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel_post_"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message.reply_text(
            preview_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == "confirm_post_":
            pending = context.user_data.get("pending_post", {})
            full_text = pending.get("full", "")
            if self.CHANNEL_ID and full_text:
                try:
                    await context.bot.send_message(
                        chat_id=self.CHANNEL_ID,
                        message_thread_id=self.TOPIC_ID,
                        text=full_text,
                        parse_mode="Markdown"
                    )
                    await query.edit_message_text("✅ Post publicado correctamente.")
                except Exception as e:
                    logger.error(f"Error al publicar en el canal: {e}")
                    await query.edit_message_text("❌ Error al publicar en el canal.")
            else:
                await query.edit_message_text("❌ No se pudo recuperar el mensaje original.")

        elif query.data == "cancel_post_":
            await query.edit_message_text("❌ Post cancelado.")

    def _generate_hashtags(self, text: str) -> str:
        text = text.lower()
        tags = []
        if any(word in text for word in ["bitcoin", "cripto", "blockchain"]):
            tags.extend(["#Cripto", "#Blockchain"])
        if any(word in text for word in ["juego", "gaming", "nft"]):
            tags.append("#GameFi")
        if any(word in text for word in ["ia", "inteligencia artificial", "modelo"]):
            tags.append("#IA")
        if any(word in text for word in ["dinero", "finanzas", "inversión"]):
            tags.append("#Finanzas")
        return " ".join(tags)
