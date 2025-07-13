from datetime import datetime, timedelta
import requests
from typing import Dict, Optional
from difflib import get_close_matches
from src.config import logger

class CryptoMapper:
    """Clase para mapeo dinámico de criptomonedas"""
    def __init__(self):
        self._mapping = self._load_base_mapping()
        self._coingecko_list = None
        self._last_update = None
    
    def _load_base_mapping(self) -> Dict[str, str]:
        """Mapeo base con las principales criptomonedas"""
        return {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum',
            'binancecoin': 'binancecoin', 'bnb': 'binancecoin',
            'ripple': 'ripple', 'xrp': 'ripple',
            'cardano': 'cardano', 'ada': 'cardano',
            'solana': 'solana', 'sol': 'solana',
            'polkadot': 'polkadot', 'dot': 'polkadot',
            'polygon': 'matic-network', 'matic': 'matic-network',
            'plant vs undead': 'plant-vs-undead-token', 'pvu': 'plant-vs-undead-token',
            'sui': 'sui',
            'bitcoin cash': 'bitcoin-cash', 'bch': 'bitcoin-cash',
        }
    
    async def fetch_coingecko_list(self):
        """Actualiza la lista desde CoinGecko"""
        try:
            response = requests.get('https://api.coingecko.com/api/v3/coins/list')
            response.raise_for_status()
            self._coingecko_list = response.json()
            self._last_update = datetime.now()
        except Exception as e:
            logger.error(f"Error al obtener lista de CoinGecko: {e}")
    
    async def maybe_refresh_list(self):
        """Actualiza la lista si es necesario"""
        if (not self._last_update or 
            (datetime.now() - self._last_update) > timedelta(hours=24)):
            await self.fetch_coingecko_list()
    
    def find_coin(self, user_input: str) -> Optional[str]:
        """Busca la criptomoneda en todas las variantes"""
        user_input = user_input.lower().strip()
        
        # 1. Buscar en mapeo local
        if user_input in self._mapping:
            return self._mapping[user_input]
        
        # 2. Buscar en lista de CoinGecko
        if self._coingecko_list:
            for coin in self._coingecko_list:
                if (user_input == coin['id'].lower() or 
                    user_input == coin['symbol'].lower()):
                    return coin['id']
        
        # 3. Búsqueda aproximada
        if self._coingecko_list:
            all_terms = [c['id'].lower() for c in self._coingecko_list] + \
                       [c['symbol'].lower() for c in self._coingecko_list]
            matches = get_close_matches(user_input, all_terms, n=1, cutoff=0.6)
            if matches:
                return matches[0]
        
        return None

# Instancia global del mapeador
crypto_mapper = CryptoMapper()