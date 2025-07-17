
from abc import ABC, abstractmethod
from communication.Hash_Algorithm import Hash_Algorithm
from communication.Message import Message
class Encryption_Scheme(ABC):
    """
        Classe astratta che rappresenta uno schema di crittografia.
        Gli schemi di crittografia devono implementare i metodi per crittografare e decrittografare i messaggi.
    """
    def __init__(self, hash_algorithm: Hash_Algorithm | None = None):
        super().__init__()
        self._hash = hash_algorithm

    @abstractmethod
    def encrypt(self, message: Message) -> Message:
        """
            Metodo per crittografare un messaggio.
        """
        pass

    @abstractmethod
    def decrypt(self, message: Message) -> Message:
        """
            Metodo per decrittografare un messaggio.
        """
        pass

    @abstractmethod
    def sign(self, message: Message) -> Message:
        """
            Metodo per applicare le proprietà di autenticità e integrità al messaggio.
        """
        pass

    @abstractmethod
    def verify(self, message: Message) -> bool:
        """
            Metodo per verificare l'autenticità e integrità di un messaggio.
        """
        pass

    @abstractmethod
    def save_on_json(self) -> dict:
        """
            Metodo per salvare lo schema di crittografia su un dizionario, da cui poi si potrà generare un file JSON.
            Deve essere implementato dalle classi derivate.
        """
        data = {}
        data['hash'] = self._hash.save_on_json() if self._hash else {}
        return data

    # @staticmethod
    # def load_from_json(data: dict):
    #     """
    #         Metodo per caricare lo schema di crittografia da un dizionario.
    #         Deve essere implementato dalle classi derivate.
    #     """
    #     # Gli import interni evitano errori di dipendenza circolare
    #     from communication.Symmetric_Scheme import Symmetric_Scheme
    #     from communication.Asymmetric_Scheme import Asymmetric_Scheme 
    #     if "private_key" not in data or "public_key" not in data:
    #         if "key" not in data:
    #             raise ValueError("[Encryption_Scheme] Dati incompleti per il caricamento dello schema di crittografia")
    #         else:
    #             return Symmetric_Scheme.load_from_json(data)
    #     else:
    #         return Asymmetric_Scheme.load_from_json(data)
        
       
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