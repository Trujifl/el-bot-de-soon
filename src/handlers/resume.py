import re
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import CallbackContext
from typing import Literal
from urllib.parse import urlparse

class ResumeHandler:
    # ==================== MÉTODOS PRINCIPALES ====================
    async def handle_resumen_texto(self, update: Update, context: CallbackContext) -> None:
        """Procesa /resumen_texto con clasificación automática"""
        original_text = update.message.text.replace('/resumen_texto', '').strip()
        
        if not original_text:
            await update.message.reply_text("✂️ Envía el texto a resumir después del comando")
            return

        content_type = self._classify_content(original_text)
        summary = self._generate_text_summary(original_text, content_type)
        
        await update.message.reply_text(
            f"📌 **Resumen ({content_type.upper()})**\n\n{summary}",
            parse_mode="Markdown"
        )

    async def handle_resumen_url(self, update: Update, context: CallbackContext) -> None:
        """Procesa /resumen_url con extracción web inteligente"""
        url = update.message.text.replace('/resumen_url', '').strip()
        
        if not url:
            await update.message.reply_text("🌐 Envía la URL después del comando")
            return

        try:
            title, clean_text = await self._fetch_web_content(url)
            content_type = self._classify_content(clean_text)
            summary = self._generate_url_summary(title, clean_text, content_type)
            
            await update.message.reply_text(
                f"🔗 **Resumen {content_type.upper()}**\n\n{summary}\n\n🌐 Fuente: {self._get_domain(url)}",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)[:200]}")

    # ==================== FUNCIONES COMPARTIDAS ====================
    def _classify_content(self, text: str) -> Literal['blockchain', 'finanzas', 'tecnología', 'general']:
        """Clasifica automáticamente el tipo de contenido"""
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

    # ==================== LÓGICA PARA TEXTO ====================
    def _generate_text_summary(self, text: str, content_type: str) -> str:
        """Genera resumen estructurado según categoría"""
        if content_type == 'blockchain':
            return self._crypto_summary(text)
        elif content_type == 'finanzas':
            return self._finance_summary(text)
        elif content_type == 'tecnología':
            return self._tech_summary(text)
        return self._general_summary(text)

    def _crypto_summary(self, text: str) -> str:
        """Resumen especializado para contenido blockchain"""
        components = {
            '🔹 Proyecto': self._extract_project_name(text),
            '💰 Tokenomics': self._extract_pattern(r'\$[\d,]+|[\d,]+% APY|\d+ tokens?', text),
            '🛠️ Mecánicas': self._extract_pattern(r'staking|minteo|gobernanza|NFT|DAO|DeFi|smart contract', text),
            '📅 Roadmap': self._extract_pattern(r'Temporada \d+|Q\d+ \d{4}|\d{4}-\d{2}', text),
            '🎯 Beneficios': self._extract_pattern(r'recompensas?|beneficios|ventajas|airdrops?|rewards', text)
        }
        return self._format_components(components)

    def _finance_summary(self, text: str) -> str:
        """Resumen para contenido financiero"""
        components = {
            '📈 Concepto': self._extract_pattern(r'mercado \w+|inversión en \w+|\w+ financiero', text),
            '💵 Montos': self._extract_pattern(r'\$[\d,]+|[\d,]+% retorno|[\d,]+ acciones', text),
            '📊 Riesgos': self._extract_pattern(r'riesgos? de \w+|volatilidad|incertidumbre', text),
            '🔄 Tendencia': self._extract_pattern(r'crecimiento|caída|estabilidad|tendencia \w+', text)
        }
        return self._format_components(components)

    def _tech_summary(self, text: str) -> str:
        """Resumen para contenido tecnológico"""
        components = {
            '🤖 Tecnología': self._extract_pattern(r'IA|blockchain|machine learning|IoT|cloud \w+', text),
            '🚀 Innovación': self._extract_pattern(r'revolución|disruptivo|nuevo paradigma', text),
            '🛠️ Funciones': self._extract_pattern(r'\w+ en tiempo real|algoritmo de \w+|\d+x más rápido', text),
            '📱 Aplicación': self._extract_pattern(r'app móvil|plataforma \w+|integración con', text)
        }
        return self._format_components(components)

    def _general_summary(self, text: str) -> str:
        """Resumen genérico estructurado"""
        key_sentences = re.findall(r'([A-Z][^.!?]*[.!?])', text)[:5]
        return "📌 Puntos clave:\n\n" + "\n".join(f"• {sentence.strip()}" for sentence in key_sentences)

    # ==================== LÓGICA PARA URLs ====================
    async def _fetch_web_content(self, url: str) -> tuple:
        """Extrae y limpia contenido web"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Limpieza avanzada
            for element in soup(['script', 'style', 'footer', 'nav', 'iframe', 'img']):
                element.decompose()
            
            title = soup.title.string if soup.title else "Contenido Web"
            
            # Extracción mejorada de contenido relevante
            content_blocks = []
            for tag in ['h1', 'h2', 'h3', 'p']:
                elements = soup.find_all(tag)
                for el in elements:
                    text = el.get_text().strip()
                    if len(text.split()) > 5:  # Solo párrafos con más de 5 palabras
                        content_blocks.append(text)
            
            return title, "\n".join(content_blocks[:15])  # Limitar a 15 bloques
            
        except Exception as e:
            raise Exception(f"No se pudo procesar la URL: {str(e)}")

    def _generate_url_summary(self, title: str, text: str, content_type: str) -> str:
        """Genera resumen web según categoría"""
        if content_type == 'blockchain':
            return self._crypto_url_summary(title, text)
        elif content_type == 'finanzas':
            return self._finance_url_summary(title, text)
        elif content_type == 'tecnología':
            return self._tech_url_summary(title, text)
        return self._general_url_summary(title, text)

    def _crypto_url_summary(self, title: str, text: str) -> str:
        """Resumen especializado para URLs blockchain"""
        components = {
            '📌 Título': title,
            '💰 Tokenomics': self._extract_pattern(r'\$[\d,]+|[\d,]+% APY|\d+ tokens?', text),
            '🔄 Mecánicas': self._extract_pattern(r'staking|minteo|gobernanza|NFT|DAO|DeFi', text),
            '🚀 Actualización': self._extract_pattern(r'lanzamiento|Temporada \d+|Q\d+ \d{4}', text),
            '🌐 Casos de Uso': self._extract_pattern(r'GameFi|Web3|Metaverso|DEX', text)
        }
        return self._format_url_components(components)

    def _finance_url_summary(self, title: str, text: str) -> str:
        """Resumen para URLs financieras"""
        components = {
            '📌 Título': title,
            '📊 Mercado': self._extract_pattern(r'mercado \w+|índice \w+|sector \w+', text),
            '📈 Análisis': self._extract_pattern(r'tendencia alcista|presión bajista|soporte en', text),
            '💡 Recomendación': self._extract_pattern(r'invertir en|evitar \w+|mantener posición', text)
        }
        return self._format_url_components(components)

    def _tech_url_summary(self, title: str, text: str) -> str:
        """Resumen para URLs tecnológicas"""
        components = {
            '📌 Título': title,
            '🤖 Tecnología': self._extract_pattern(r'IA generativa|\d+nm chip|computación cuántica', text),
            '🔄 Impacto': self._extract_pattern(r'revolucionar \w+|cambiar la industria', text),
            '📱 Aplicación': self._extract_pattern(r'app móvil|plataforma \w+|integración con', text)
        }
        return self._format_url_components(components)

    def _general_url_summary(self, title: str, text: str) -> str:
        """Resumen genérico para URLs"""
        key_points = re.findall(r'([A-Z][^.!?]*[.!?])', text)[:5]
        return f"📌 {title}\n\n" + "🔹 " + "\n🔹 ".join(key_points[:5])

    # ==================== FUNCIONES AUXILIARES ====================
    def _extract_project_name(self, text: str) -> str:
        """Extrae nombres de proyectos (mayúsculas iniciales)"""
        matches = re.findall(r'\b([A-Z][a-zA-Z0-9]+)\b', text)
        return matches[0] if matches else "Proyecto"

    def _extract_pattern(self, pattern: str, text: str) -> str:
        """Extrae elementos con patrón específico"""
        matches = re.findall(pattern, text, re.IGNORECASE)
        unique_matches = list(dict.fromkeys(matches))[:3]  # Eliminar duplicados
        return "\n".join(f"- {m}" for m in unique_matches) if unique_matches else "No especificado"

    def _format_components(self, components: dict) -> str:
        """Da formato a los componentes del resumen"""
        return "\n".join(
            f"{key}: {value}" 
            for key, value in components.items() 
            if value != "No especificado"
        ) + "\n\n🔍 Resumen generado automáticamente"

    def _format_url_components(self, components: dict) -> str:
        """Formatea componentes para URLs"""
        return "\n".join(
            f"{key}: {value}" 
            for key, value in components.items() 
            if value and value != "No especificado"
        ) + "\n\n📌 Resumen automático"

    def _get_domain(self, url: str) -> str:
        """Extrae dominio limpio para mostrar"""
        domain = urlparse(url).netloc
        clean_domain = domain.replace("www.", "").split(".")[0]
        return clean_domain.capitalize()