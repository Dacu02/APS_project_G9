from abc import ABC, abstractmethod
from communication.Message import Message

class MAC_Algorithm(ABC):
    """
    Classe astratta che rappresenta un algoritmo MAC (Message Authentication Code).
    Gli algoritmi MAC devono implementare i metodi per calcolare e verificare il codice di autenticazione del messaggio.
    """
    
    @abstractmethod
    def calculate_mac(self, message: Message) -> str:
        """
        Calcola il codice di autenticazione del messaggio.
        """
        pass

    @abstractmethod
    def verify_mac(self, message: Message, mac: str) -> bool:
        """
        Verifica se il codice di autenticazione del messaggio è valido.
        """
        pass

    @abstractmethod
    def save_on_json(self) -> dict:
        """
        Salva l'algoritmo MAC su un dizionario, da cui poi si potrà generare un file JSON.
        """
        pass

    @staticmethod
    @abstractmethod
    def load_from_json(data: dict) -> 'MAC_Algorithm':
        """
        Carica l'algoritmo MAC da un dizionario.
        Deve essere implementato dalle classi derivate.
        """
        data_type = data.get("type")
        pass #TODO Continua usando il type
