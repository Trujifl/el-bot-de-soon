def construir_contexto_opinion(token: dict) -> dict:
    """
    Construye un contexto para IA con los datos del token.
    """
    return {
        "cripto": {
            "nombre": token.get("nombre", "Token"),
            "simbolo": token.get("simbolo", "???").upper(),
            "precio": token.get("precio", 0),
            "cambio_24h": token.get("cambio_24h", 0)
        }
    }

def armar_prompt_opinion(token: dict) -> str:
    """
    Genera un prompt para que la IA opine sobre una cripto.
    Usa estilo profesional con un toque de humor y emojis sobrios.
    """
    nombre = token.get("nombre", "Token")
    simbolo = token.get("simbolo", "???").upper()
    precio = token.get("precio", 0)
    cambio = token.get("cambio_24h", 0)

    tendencia = "📈" if cambio >= 5 else "📉" if cambio <= -5 else "📊"

    intro = (
        f"Hoy, {nombre} ({simbolo}) cotiza a ${precio:,.2f} USD "
        f"con una variación de {cambio:+.2f}% en las últimas 24 horas. {tendencia}\n\n"
    )

    instrucciones = (
        "Actúa como un analista financiero profesional que responde en tono breve, claro, "
        "con un toque ligero de humor (sin exagerar) y usando uno o dos emojis sutiles. "
        "No seas alarmista. Habla como si le explicaras a una comunidad cripto en Telegram.\n\n"
        "¿Cuál es tu opinión sobre el comportamiento de este token hoy?"
    )

    return intro + instrucciones
