from abc import ABC, abstractmethod
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

    def __init__(self, key: Key | None = None):
        super().__init__()
        self._key = key

    def get_key(self) -> Key | None:
        return self._key
    
    def save_on_json(self) -> dict:
        return {
            "key": str(self._key)
        }

    def load_on_json(self, data: dict):
        self._key = Key.load_from_json(data["key"])