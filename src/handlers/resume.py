from telegram import Update
from telegram.ext import CallbackContext
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from src.services.openai import generar_respuesta_ia

class ResumeHandler:
    async def handle_resumen_texto(self, update: Update, context: CallbackContext) -> None:
        original_text = update.message.text.replace('/resumen_texto', '').strip()

        if not original_text:
            await update.message.reply_text(
                "📝 *Instrucciones para /resumen_texto:*\n\n"
                "Envía el comando seguido del texto que deseas resumir:\n"
                "Ejemplo:\n"
                "`/resumen_texto Bitcoin es una criptomoneda descentralizada...`",
                parse_mode="Markdown"
            )
            return

        try:
            content_type = self._classify_content(original_text)
            prompt = self._build_prompt(original_text, content_type)
            summary = await generar_respuesta_ia(prompt, update.effective_user.first_name, original_text)
            await update.message.reply_text(summary, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al generar resumen: {str(e)}")

    async def handle_resumen_url(self, update: Update, context: CallbackContext) -> None:
        url = update.message.text.replace('/resumen_url', '').strip()

        if not url:
            await update.message.reply_text(
                "🌐 *Instrucciones para /resumen_url:*\n\n"
                "Envía el comando seguido de la URL que deseas resumir:\n"
                "Ejemplo:\n"
                "`/resumen_url https://ejemplo.com/articulo-cripto`",
                parse_mode="Markdown"
            )
            return

        try:
            title, content = self._fetch_url_content(url)
            content_type = self._classify_content(content)
            prompt = self._build_prompt(content, content_type)
            summary = await generar_respuesta_ia(prompt, update.effective_user.first_name, content)

            await update.message.reply_text(
                f"🔗 *Resumen de {title}*\n\n{summary}\n\n🌐 Fuente: {self._get_domain(url)}",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error al procesar URL: {str(e)}")

    def _classify_content(self, text: str) -> str:
        text_lower = text.lower()
        if any(term in text_lower for term in ['blockchain', 'token', 'nft', 'web3', 'defi', 'staking']):
            return 'blockchain'
        if any(term in text_lower for term in ['inversión', 'mercado', 'acciones', 'dividendos', 'trading']):
            return 'finanzas'
        if any(term in text_lower for term in ['inteligencia artificial', 'machine learning', 'software', 'algoritmo']):
            return 'tecnología'
        return 'general'

    def _build_prompt(self, texto: str, tipo: str) -> str:
        introduccion = (
            "Eres un analista profesional. Tu tarea es generar un resumen detallado y estructurado "
            "en español del siguiente contenido. El resumen debe estar organizado por secciones claras "
            "según el tipo de tema detectado."
        )
