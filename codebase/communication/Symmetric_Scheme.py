from abc import ABC, abstractmethod
from communication.MAC_Algorithm import MAC_Algorithm
from communication.Encryption_Scheme import Encryption_Scheme
from communication.Message import Message
from communication.Key import Key

class Symmetric_Scheme(Encryption_Scheme, ABC):
    """
        Schema di crittografia simmetrica, eredita Encryption_Scheme.
        Utilizza una singola chiave per cifrare e decifrare i messaggi.
    """
    @abstractmethod
    def encrypt(self, message: Message) -> Message:
        pass

    @abstractmethod
    def decrypt(self, message: Message) -> Message:
        pass

    @abstractmethod
    def sign(self, message: Message) -> Message:
        pass

    @abstractmethod
    def verify(self, message: Message) -> bool:
        pass

    def __init__(self, key: Key | None = None, mac_algorithm: MAC_Algorithm | None = None):
        super().__init__()
        self._key = key
        self._mac_algorithm = mac_algorithm

    def get_key(self) -> Key | None:
        return self._key
    
    def save_on_json(self) -> dict:
        data = {}
        data["key"] = self._key.save_on_json() if self._key else None
        return data

    @staticmethod
    def load_from_json(data: dict) -> 'Symmetric_Scheme':
        if "scheme_type" in data:
            name = data["scheme_type"]
            if name == "Cipher_Block_Chaining":
                from communication.Cipher_Block_Chaining import Cipher_Block_Chaining
                return Cipher_Block_Chaining.load_from_json(data)
            else:
                raise ValueError(f"Tipo di schema di crittografia sconosciuto: {name}")
        raise ValueError("Non implementato")

    def set_MAC_algorithm(self, mac_algorithm: MAC_Algorithm) -> None:
        """
            Imposta l'algoritmo di autenticazione dei messaggi (MAC).
        """
        self._mac_algorithm = mac_algorithm
