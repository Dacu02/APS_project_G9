from __future__ import annotations
from abc import abstractmethod
from pyparsing import ABC
from communication.Encryption_Scheme import Encryption_Scheme
from communication.Message import Message
from communication.Key import Key
class Asymmetric_Scheme(Encryption_Scheme, ABC):
    """
        Schema di crittografia asimmetrica, eredita Encryption_Scheme.
        Utilizza una coppia di chiavi: una pubblica ed una privata.
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

    def __init__(self, private_key: Key|None = None, public_key: Key|None = None):
        super().__init__()
        self._private_key = private_key
        self._public_key = public_key

    def get_private_key(self) -> Key | None:
        return self._private_key

    def get_public_key(self) -> Key | None:
        return self._public_key
    
    def save_on_json(self) -> dict:
        return {
            "private_key": self._private_key.save_on_json() if self._private_key else None,
            "public_key": self._public_key.save_on_json() if self._public_key else None
        }
    
    # @staticmethod
    # def load_from_json(data: dict):
    #     self._private_key = Key.load_from_json(data["private_key"])
    #     self._public_key = Key.load_from_json(data["public_key"])

    @abstractmethod
    def share_public_key(self) -> Asymmetric_Scheme | None:
        """
            Restituisce lo schema di crittografia con la sola chiave pubblica.
        """
        pass