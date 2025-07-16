class Key:
    """
    Classe che rappresenta una chiave crittografica.
    """
    def __init__(self, key_data: bytes):
        self._key_data = key_data

    def get_key(self) -> bytes:
        return self._key_data
    
    def save_on_json(self) -> dict:
        return {
            "key": self._key_data.hex()  # Conversione a hex per la serializzazione JSON
        }
    
    @staticmethod
    def load_from_json(data: dict) -> 'Key':
        key_data = bytes.fromhex(data["key"])
        return Key(key_data)