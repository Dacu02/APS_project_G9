from abc import ABC, abstractmethod
from communication.Hash_Algorithm import Hash_Algorithm
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

    # @staticmethod
    # def load_from_json(data: dict):
    #     key = Key.load_from_json(data["key"])
    #     if "hash" in data:
    #         hash_algorithm = Hash_Algorithm.load_from_json(data["hash"])
    #     return Symmetric_Scheme(key=key, hash=hash_algorithm)