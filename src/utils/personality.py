"""
Módulo de Personalidad del Bot - SoonBot v9.4

Contiene:
1. Generación de respuestas con estilo único
2. Sistema de frases contextuales
3. Manejo de emociones básicas
"""

import random
from typing import Optional
from datetime import datetime
from src.config import BotPersonality, logger
from src.services.openai import generar_respuesta_ia

class Personalidad: 
    @staticmethod
    def generar_saludo(nombre: str) -> str:
        """Genera un saludo casual con el estilo del bot"""
        saludos = [
            f"¡Epa {nombre}! ¿Cómo anda, todo bien? 👊",
            f"¡Buenaas {nombre}! ¿En qué te ayudo? 🔥",
            f"¡Buenas crack!!! Dime cómo colaboramos hoy 💼",
            f"¡Que pasaaa {nombre}! Listo para lo que necesites ⚡"
        ]
        return random.choice(saludos)

    @staticmethod
    def generar_despedida(nombre: str) -> str:
        """Genera una despedida con personalidad"""
        despedidas = [
            f"¡Listo socio! Cualquier cosa me chiflas 👌",
            f"Nos vemos {nombre}, no te quedes ghosteando 👻",
            f"Hasta luego, ¡que no se te caiga el exchange! 😎",
            f"Chao pescao, éxito en esas inversiones 🐟"
        ]
        return random.choice(despedidas)

    @staticmethod
    def generar_respuesta_positiva() -> str:
        """Respuestas para acciones exitosas"""
        frases = [
            "¡Juega vivo! Así me gusta 😏",
            "¡Esooo Excelente! Apretaste el botón correcto 🤙",
            "¡Confirmado! Más rápido que transacción en Solana ⚡",
            "¡Listo! Más fácil que minar con ASIC ✅"
        ]
        return random.choice(frases)

    @staticmethod
    def generar_respuesta_error(nombre: str) -> str:
        """Mensajes de error con estilo"""
        errores = [
            f"¡Chale {nombre}! Algo se bugueó 😅 ¿Le damos F5?",
            "Error 404 - Aquí no hay crypto... pero reintentemos 🔄",
            "Se cayó como LUNA... pero ya lo reseteamos 🌕",
            "¡Ups! Parece que me doxxearon... broma, reintenta 👀"
        ]
        return random.choice(errores)

    @staticmethod
    def generar_mensaje_espera() -> str:
        """Mensajes mientras se procesa algo"""
        mensajes = [
            "Tranqui, no es rugpull... procesando 🕵️",
            "Espera espera, como en ICO... cargando 📈",
            "Mándame un memecoin mientras esperas... trabajando 🐶",
            "Más rápido que Binance en caída... pero dame un toque ⏳"
        ]
        return random.choice(mensajes)

    @staticmethod
    def generar_respuesta_cripto(cripto: str, accion: str) -> Optional[str]:
        """Respuestas contextuales sobre criptomonedas"""
        cripto = cripto.lower()
        respuestas = {
            "bitcoin": [
                f"Ahhh el rey {cripto} 👑, dime qué necesitas saber",
                f"BTC, el oro digital 🏆, ¿qué te interesa?"
            ],
            "ethereum": [
                f"{cripto.capitalize()} y su mundo DeFi 🏦",
                f"ETH, el combustible de los smart contracts ⛽"
            ],
            "inversion": [
                f"¿Pensando en invertir en {cripto}? 💰 Te doy data:",
                f"Antes de comprar {cripto}, considera:"
            ],
            "general": [
                f"¡{cripto.capitalize()} en el radar! 📡",
                f"Interesante lo de {cripto}, dime más..."
            ]
        }
        
        if cripto in respuestas:
            return random.choice(respuestas[cripto])
        elif accion in respuestas:
            return random.choice(respuestas[accion])
        else:
            return random.choice(respuestas["general"])

    @staticmethod
    def generar_respuesta_temporal() -> str:
        """Respuestas que varían según hora del día"""
        hora = datetime.now().hour
        if 5 <= hora < 12:
            return "¡Buenos días cryptoamigo! ☀️ ¿En qué onda?"
        elif 12 <= hora < 19:
            return "¡Buenas tardes! ¿Cómo va el trading? 📊"
        else:
            return "¡Buena noche! ¿Analizando charts? 🌙"

    @staticmethod
    def responder(mensaje: str, nombre_usuario: str, contexto: str = None) -> str:
        """
        Sistema centralizado de respuestas.
        
        Parámetros:
            mensaje: Texto del usuario
            nombre_usuario: Nombre para personalizar
            contexto: 'precio', 'inversion', etc.
        """
        mensaje = mensaje.lower()

    @staticmethod
    async def generar_respuesta_avanzada(mensaje: str, nombre_usuario: str, contexto: str = None) -> str:
        """Usa OpenAI para respuestas conversacionales avanzadas"""
        try:
            # 1. Primero intenta con respuestas predefinidas
            respuesta_predefinida = Personalidad.responder(mensaje, nombre_usuario, contexto)
            if "no entendí" not in respuesta_predefinida.lower():
                return respuesta_predefinida
            
            # 2. Si no hay respuesta predefinida adecuada, usa OpenAI
            respuesta_ia = await generar_respuesta_ia(
                mensaje=mensaje,
                contexto=contexto,
                nombre_usuario=nombre_usuario
            )
            return respuesta_ia or Personalidad.generar_respuesta_error(nombre_usuario)
            
        except Exception as e:
            logger.error(f"Error al generar respuesta: {e}")
            return Personalidad.generar_respuesta_error(nombre_usuario)
        
        