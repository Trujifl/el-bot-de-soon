"""
Clasificador de Intenciones para Mensajes de Usuario
"""
from typing import Optional, Dict, List, Literal

IntentType = Literal[
    "saludo", 
    "precio", 
    "inversion", 
    "mercado", 
    "ayuda", 
    "resumen", 
    "otro"
]

class CryptoIntentClassifier:
    @staticmethod
    def classify_intent(text: str) -> IntentType:
        """Clasifica la intención del mensaje del usuario"""
        text = text.lower()

        # Detección de saludos
        if any(greeting in text for greeting in ["hola", "buenas", "hi", "hello", "saludos"]):
            return "saludo"

        # Detección de consultas de precio
        price_terms = ["precio", "valor", "cotización", "cuánto está", "cómo está", "price"]
        if any(term in text for term in price_terms):
            return "precio"

        # Detección de consultas de inversión
        investment_terms = ["invertir", "comprar", "vender", "inversión", "trading"]
        if any(term in text for term in investment_terms):
            return "inversion"

        # Detección de consultas de mercado
        market_terms = ["mercado", "tendencia", "análisis", "predicción", "cómo va"]
        if any(term in text for term in market_terms):
            return "mercado"

        # Detección de solicitudes de ayuda
        help_terms = ["ayuda", "help", "comandos", "qué puedes hacer"]
        if any(term in text for term in help_terms):
            return "ayuda"

        # Detección de solicitudes de resumen
        summary_terms = ["resumen", "resumir", "sumarizar", "summary"]
        if any(term in text for term in summary_terms):
            return "resumen"

        return "otro"

    @staticmethod
    def detectar_cripto(text: str) -> Optional[str]:
        """Detecta menciones de criptomonedas comunes con alias"""
        # Diccionario de alias comunes
        alias_criptos = {
            "btc": "bitcoin",
            "bitcoin": "bitcoin",
            "eth": "ethereum",
            "ethereum": "ethereum",
            "bnb": "binancecoin",
            "sol": "solana",
            "ada": "cardano"
        }
        
        text = text.lower()
        for alias, cripto in alias_criptos.items():
            if alias in text:
                return cripto
        return None