import pytest
from src.utils.classifier import CryptoIntentClassifier


@pytest.mark.parametrize("text,expected", [
    ("Hola bot", "saludo"),
    ("¿Qué precio tiene Bitcoin?", "precio"),
    ("Quiero invertir en Ethereum", "inversion"),
    ("Cómo está el mercado hoy?", "mercado"),
    ("Ayuda con el bot", "ayuda"),
    ("Resume este artículo", "resumen"),
    ("Noticias recientes", "otro"),
])
def test_classify_intent(text, expected):
    assert CryptoIntentClassifier.classify_intent(text) == expected

@pytest.mark.parametrize("text,expected", [
    ("Comprar BTC", "bitcoin"),
    ("Precio del ETH", "ethereum"),
    ("Cómo está solana?", "solana"),
    ("Noticias de cardano", "cardano"),
    ("Hola mundo", None),
])
def test_detect_cripto(text, expected):
    assert CryptoIntentClassifier.detect_cripto_mention(text) == expected