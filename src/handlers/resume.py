import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CallbackContext
from typing import Literal
from urllib.parse import urlparse
from src.services.openai import generar_respuesta_ia

class ResumeHandler:
    async def handle_resumen_texto(self, update: Update, context: CallbackContext) -> None:
        original_text = ' '.join(context.args).strip()

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
            summary = await self._generate_openai_summary(original_text, content_type)
            for chunk in self._split_message(summary):
                await update.message.reply_text(chunk, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al generar resumen: {str(e)}")

    async def handle_resumen_url(self, update: Update, context: CallbackContext) -> None:
        url = ' '.join(context.args).strip()

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
            title, clean_text = await self._fetch_web_content(url)
            content_type = self._classify_content(clean_text)
            summary = await self._generate_openai_summary(clean_text, content_type)
            fuente = self._get_domain(url)
            full_message = f"🔗 **Resumen de {title}**\n\n{summary}\n\n🌐 Fuente: {fuente}"
            for chunk in self._split_message(full_message):
                await update.message.reply_text(chunk, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception as e:
            await update.message.reply_text(f"❌ Error al procesar URL: {str(e)}")

    def _split_message(self, text: str, limit: int = 4000) -> list[str]:
        chunks = []
        while len(text) > limit:
            split_at = text.rfind('\n', 0, limit)
            if split_at == -1:
                split_at = limit
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip()
        chunks.append(text)
        return chunks

    def _classify_content(self, text: str) -> Literal['blockchain', 'finanzas', 'tecnología', 'general']:
        crypto_terms = ['blockchain', 'token', 'nft', 'web3', 'defi', 'staking', 'smart contract', 'wallet']
        finance_terms = ['inversión', 'mercado', 'acciones', 'dividendos', 'bolsa', 'financiero', 'trading']
        tech_terms = ['IA', 'machine learning', 'cloud', 'software', 'hardware', 'algoritmo']

        text_lower = text.lower()

        if any(term in text_lower for term in crypto_terms):
            return 'blockchain'
        elif any(term in text_lower for term in finance_terms):
            return 'finanzas'
        elif any(term in text_lower for term in tech_terms):
            return 'tecnología'
        return 'general'

    async def _generate_openai_summary(self, text: str, tipo: str) -> str:
        if tipo == 'blockchain':
            instrucciones = """🔹 Proyecto
Breve descripción general del proyecto

💰 Tokenomics
Aspectos financieros del token como utilidad, emisión, valor o circulación

🛠️ Mecánicas
Mecanismos de funcionamiento, tecnología o contratos inteligentes

🗓️ Roadmap
Fechas clave, hitos futuros o versiones planificadas

🎯 Beneficios
Ventajas, recompensas, incentivos o atractivo para la comunidad"""
        elif tipo == 'finanzas':
            instrucciones = """📈 Concepto
Tema principal y su aplicación

💵 Montos
Datos numéricos relevantes o condiciones económicas

📊 Riesgos
Factores de volatilidad, incertidumbre o advertencias

🔄 Tendencia
Dirección reciente o proyectada del fenómeno financiero"""
        elif tipo == 'tecnología':
            instrucciones = """🤖 Tecnología
Nombre y naturaleza de la innovación

🚀 Innovación
Qué la hace diferente o disruptiva

🛠️ Funciones
Para qué sirve y cómo funciona

📱 Aplicación
Casos de uso o entornos donde se implementa"""
        else:
            instrucciones = """🔹 Puntos clave
Resumen general con ideas principales y conceptos destacados
Usa viñetas y encabezados solo si es necesario"""

        prompt = (
            "Eres un asistente profesional que redacta resúmenes temáticos con formato visual estructurado. "
            "Tu respuesta debe estar en español y seguir exactamente este formato, usando encabezados con emojis. "
            "No agregues introducciones ni conclusiones. Si alguna sección no aplica, indica 'No especificado'. "
            "Cada sección debe estar separada por una línea en blanco. \n\n"
            f"{instrucciones}\n\nTexto a resumir:\n{text}\n\n"
            "📌 Resumen generado automáticamente."
        )

        return await generar_respuesta_ia(prompt, "Usuario")

    async def _fetch_web_content(self, url: str) -> tuple:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'es-ES,es;q=0.9'
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(['script', 'style', 'footer', 'nav', 'iframe', 'img']):
                element.decompose()
            title = soup.title.string if soup.title else "Contenido Web"
            content_blocks = []
            for tag in ['h1', 'h2', 'h3', 'p']:
                elements = soup.find_all(tag)
                for el in elements:
                    text = el.get_text().strip()
                    if len(text.split()) > 5:
                        content_blocks.append(text)
            return title, "\n".join(content_blocks[:30])
        except Exception as e:
            raise Exception(f"No se pudo procesar la URL: {str(e)}")

    def _get_domain(self, url: str) -> str:
        domain = urlparse(url).netloc
        clean_domain = domain.replace("www.", "").split(".")[0]
        return clean_domain.capitalize()
