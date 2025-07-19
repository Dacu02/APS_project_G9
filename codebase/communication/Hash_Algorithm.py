from abc import ABC, abstractmethod



class Hash_Algorithm(ABC):
    """
        Classe astratta che rappresenta un algoritmo di hash.
        Gli algoritmi di hash devono implementare i metodi per calcolare l'hash di una stringa.
    """
    @abstractmethod
    def hash(self, data: str) -> str:
        """
            Restituisce l'hash della stringa data.
        """
        pass

    @abstractmethod
    def save_on_json(self) -> dict:
        """
            Restituisce una rappresentazione JSON dell'algoritmo di hash.
        """
        pass

    @staticmethod
    def load_from_json(data: dict) -> "Hash_Algorithm":
        from communication.Generic_Hash_Algorithm import Generic_Hash_Algorithm
        """
            Carica un algoritmo di hash da una rappresentazione JSON.
        """
        return Generic_Hash_Algorithm.load_from_json(data)