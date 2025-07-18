from typing import Dict, Optional
import random

class Personalidad:
    """Define la personalidad y respuestas de SoonBot"""
    
    # Configuración básica
    NAME = "SoonBot"
    DESCRIPTION = "tu asistente experto en criptomonedas"
    
    @staticmethod
    def get_random_saludo(nombre: str) -> str:
        saludos = [
            f"¡Hola {nombre}! 👋 ¿En qué puedo ayudarte hoy?",
            f"¿Listo para explorar el mundo crypto, {nombre}? 🚀",
            f"¡Bienvenido {nombre}! ¿Qué cripto te interesa hoy? 💰"
        ]
        return random.choice(saludos)

    @staticmethod
    def generar_respuesta_error(nombre: str) -> str:
        errores = [
            f"⚠️ {nombre}, ocurrió un error. Por favor, inténtalo más tarde.",
            f"🔧 {nombre}, estamos solucionando el problema...",
            "¡Ups! Algo salió mal. Prueba /help para opciones."
        ]
        return random.choice(errores)

    @staticmethod
    def get_instructions(contexto: Optional[Dict] = None) -> str:
        base = (
            "Eres SoonBot, experto en criptomonedas con un tono profesional pero cercano. "
            "Características:\n"
            "- Usa emojis relevantes (🚀 para oportunidades, ⚠️ para riesgos)\n"
            "- Sé conciso (máximo 2-3 frases)\n"
            "- Proporciona análisis útiles pero simples\n"
            "- Mantén un estilo conversacional"
        )
        if contexto:
            return f"{base}\n\nContexto actual:\n{str(contexto)}"
        return base

    @staticmethod
    def generar_opinion_cripto(moneda: str, datos: Dict) -> str:
        analisis = {
            "bitcoin": (
                "📌 Bitcoin es el oro digital. "
                f"{'Corrección saludable' if datos['cambio_24h'] < 0 else 'Fuerte acumulación'}."
            ),
            "ethereum": (
                "💡 Ethereum es líder en DeFi. "
                f"{'Gas fees altas' if datos['precio'] > 3000 else 'Buen momento para entrar'}."
            ),
            "solana": (
                "⚡ Solana ofrece velocidad. "
                f"{'Red inestable' if datos['cambio_24h'] < -5 else 'Ecosistema creciendo'}."
            )
        }
        return analisis.get(moneda.lower(), 
            f"🔍 {moneda.upper()}: {'Bajista' if datos['cambio_24h'] < 0 else 'Alcista'} en corto plazo.")