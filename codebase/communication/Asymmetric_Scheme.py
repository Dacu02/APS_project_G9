from __future__ import annotations
from abc import abstractmethod
from pyparsing import ABC
from communication.Hash_Algorithm import Hash_Algorithm
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

    @abstractmethod
    def authority_sign(self, message: Message) -> Message:
        """
            Firma il messaggio utilizzando la chiave privata dell'utente.
            Utilizzato per garantire l'autenticità del messaggio.
        """
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
        data = {}
        data["private_key"] = self._private_key.save_on_json() if self._private_key else None
        data["public_key"] = self._public_key.save_on_json() if self._public_key else None
        return data

    @staticmethod
    def load_from_json(data: dict) -> 'Asymmetric_Scheme':
        if "scheme_type" in data:
            name = data["scheme_type"]
            if name == "Parametric_Asymmetric_Scheme":
                from communication.Parametric_Asymmetric_Scheme import Parametric_Asymmetric_Scheme
                return Parametric_Asymmetric_Scheme.load_from_json(data)
            else:
                raise ValueError(f"Tipo di schema di crittografia sconosciuto: {name}")
        else:
            raise ValueError("Schema non leggibile")

    @abstractmethod
    def share_public_key(self) -> Asymmetric_Scheme | None:
        """
            Restituisce lo schema di crittografia con la sola chiave pubblica.
        """
        pass

    def hash(self, data:str) -> str:
        """
            Restituisce l'hash della stringa data.
            Utilizza la chiave privata per calcolare l'hash.
        """
        if self._hash is None:
            raise ValueError("[Encryption_Scheme] Algoritmo di hash non impostato")

        return self._hash.hash(data)

    def set_hash_algorithm(self, hash_algorithm: Hash_Algorithm):
        """
            Imposta l'algoritmo di hash da utilizzare per calcolare l'hash dei messaggi.
        """
        self._hash = hash_algorithm

    def get_hash_algorithm(self) -> Hash_Algorithm | None:
        """
            Restituisce l'algoritmo di hash utilizzato per calcolare l'hash dei messaggi.
        """
        return self._hash