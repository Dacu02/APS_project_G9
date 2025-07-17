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
        data = super().save_on_json()
        data["key"] = str(self._key)
        return data

    @staticmethod
    def load_from_json(data: dict) -> 'Symmetric_Scheme':
        if "scheme_type" in data:
            name = data["scheme_type"]
            #TODO in base al name passalo ad una classe specifica
        raise ValueError("Non implementato")

    def set_MAC_algorithm(self, mac_algorithm: MAC_Algorithm) -> None:
        """
            Imposta l'algoritmo di autenticazione dei messaggi (MAC).
        """
        self._mac_algorithm = mac_algorithm
