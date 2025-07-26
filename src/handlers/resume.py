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
            summary = self._generate_text_summary(original_text, content_type)
            await update.message.reply_text(summary, parse_mode="Markdown")
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
            summary = self._generate_url_summary(title, clean_text, content_type)
            await update.message.reply_text(
                f"🔗 **Resumen de {title}**\n\n{summary}\n\n🌐 Fuente: {self._get_domain(url)}",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Error al procesar URL: {str(e)}")

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

    def _generate_text_summary(self, text: str, content_type: str) -> str:
        if content_type == 'blockchain':
            return self._crypto_summary(text)
        elif content_type == 'finanzas':
            return self._finance_summary(text)
        elif content_type == 'tecnología':
            return self._tech_summary(text)
        return self._general_summary(text)

    def _crypto_summary(self, text: str) -> str:
        components = {
            '🔹 Proyecto': self._extract_project_name(text),
            '💰 Tokenomics': self._extract_pattern(r'\$[\d,]+|[\d,]+% APY|\d+ tokens?', text),
            '🛠️ Mecánicas': self._extract_pattern(r'staking|minteo|gobernanza|NFT|DAO|DeFi|smart contract', text),
            '📅 Roadmap': self._extract_pattern(r'Temporada \d+|Q\d+ \d{4}|\d{4}-\d{2}', text),
            '🎯 Beneficios': self._extract_pattern(r'recompensas?|beneficios|ventajas|airdrops?|rewards', text)
        }
        return self._format_components(components)

    def _finance_summary(self, text: str) -> str:
        components = {
            '📈 Concepto': self._extract_pattern(r'mercado \w+|inversión en \w+|\w+ financiero', text),
            '💵 Montos': self._extract_pattern(r'\$[\d,]+|[\d,]+% retorno|[\d,]+ acciones', text),
            '📊 Riesgos': self._extract_pattern(r'riesgos? de \w+|volatilidad|incertidumbre', text),
            '🔄 Tendencia': self._extract_pattern(r'crecimiento|caída|estabilidad|tendencia \w+', text)
        }
        return self._format_components(components)

    def _tech_summary(self, text: str) -> str:
        components = {
            '🤖 Tecnología': self._extract_pattern(r'IA|blockchain|machine learning|IoT|cloud \w+', text),
            '🚀 Innovación': self._extract_pattern(r'revolución|disruptivo|nuevo paradigma', text),
            '🛠️ Funciones': self._extract_pattern(r'\w+ en tiempo real|algoritmo de \w+|\d+x más rápido', text),
            '📱 Aplicación': self._extract_pattern(r'app móvil|plataforma \w+|integración con', text)
        }
        return self._format_components(components)

    def _general_summary(self, text: str) -> str:
        key_sentences = re.findall(r'([A-Z][^.!?]*[.!?])', text)[:5]
        return "📌 Puntos clave:\n\n" + "\n".join(f"• {sentence.strip()}" for sentence in key_sentences)

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
            return title, "\n".join(content_blocks[:15])
        except Exception as e:
            raise Exception(f"No se pudo procesar la URL: {str(e)}")

    def _generate_url_summary(self, title: str, text: str, content_type: str) -> str:
        if content_type == 'blockchain':
            return self._crypto_url_summary(title, text)
        elif content_type == 'finanzas':
            return self._finance_url_summary(title, text)
        elif content_type == 'tecnología':
            return self._tech_url_summary(title, text)
        return self._general_url_summary(title, text)

    def _crypto_url_summary(self, title: str, text: str) -> str:
        components = {
            '📌 Título': title,
            '💰 Tokenomics': self._extract_pattern(r'\$[\d,]+|[\d,]+% APY|\d+ tokens?', text),
            '🔄 Mecánicas': self._extract_pattern(r'staking|minteo|gobernanza|NFT|DAO|DeFi', text),
            '🚀 Actualización': self._extract_pattern(r'lanzamiento|Temporada \d+|Q\d+ \d{4}', text),
            '🌐 Casos de Uso': self._extract_pattern(r'GameFi|Web3|Metaverso|DEX', text)
        }
        return self._format_url_components(components)

    def _finance_url_summary(self, title: str, text: str) -> str:
        components = {
            '📌 Título': title,
            '📊 Mercado': self._extract_pattern(r'mercado \w+|índice \w+|sector \w+', text),
            '📈 Análisis': self._extract_pattern(r'tendencia alcista|presión bajista|soporte en', text),
            '💡 Recomendación': self._extract_pattern(r'invertir en|evitar \w+|mantener posición', text)
        }
        return self._format_url_components(components)

    def _tech_url_summary(self, title: str, text: str) -> str:
        components = {
            '📌 Título': title,
            '🤖 Tecnología': self._extract_pattern(r'IA generativa|\d+nm chip|computación cuántica', text),
            '🔄 Impacto': self._extract_pattern(r'revolucionar \w+|cambiar la industria', text),
            '📱 Aplicación': self._extract_pattern(r'app móvil|plataforma \w+|integración con', text)
        }
        return self._format_url_components(components)

    def _general_url_summary(self, title: str, text: str) -> str:
        key_points = re.findall(r'([A-Z][^.!?]*[.!?])', text)[:5]
        return f"📌 {title}\n\n" + "🔹 " + "\n🔹 ".join(key_points[:5])

    def _extract_project_name(self, text: str) -> str:
        matches = re.findall(r'\b([A-Z][a-zA-Z0-9]+)\b', text)
        return matches[0] if matches else "Proyecto"

    def _extract_pattern(self, pattern: str, text: str) -> str:
        matches = re.findall(pattern, text, re.IGNORECASE)
        unique_matches = list(dict.fromkeys(matches))[:3]
        return "\n".join(f"- {m}" for m in unique_matches) if unique_matches else "No especificado"

    def _format_components(self, components: dict) -> str:
        return "\n\n".join(
            f"{key}:\n{value}"
            for key, value in components.items()
            if value != "No especificado"
        ) + "\n\n📌 Resumen generado automáticamente"

    def _format_url_components(self, components: dict) -> str:
        return "\n\n".join(
            f"{key}:\n{value}"
            for key, value in components.items()
            if value and value != "No especificado"
        ) + "\n\n📌 Resumen automático"

    def _get_domain(self, url: str) -> str:
        domain = urlparse(url).netloc
        clean_domain = domain.replace("www.", "").split(".")[0]
        return clean_domain.capitalize()
