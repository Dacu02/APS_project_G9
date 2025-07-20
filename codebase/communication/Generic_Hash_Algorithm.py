import hashlib
from communication.Hash_Algorithm import Hash_Algorithm

class Generic_Hash_Algorithm(Hash_Algorithm):
    """
    Implementazione generica di un algoritmo di hash.
    Utilizza la libreria hashlib per supportare vari algoritmi di hash.
    """
    def __init__(self, algorithm_name:str):
        """
        Inizializza l'algoritmo di hash con il nome specificato.

        Args:
            algorithm_name: Il nome dell'algoritmo da usare (es. 'sha256', 'sha512').

        Raises:
            ValueError: Se l'algoritmo specificato non è supportato da hashlib.
        """
        super().__init__()

        self._algorithm_name = algorithm_name.lower()
        if self._algorithm_name not in hashlib.algorithms_available:
            raise ValueError(f"Algoritmo di hash '{self._algorithm_name}' non supportato, disponibili: {hashlib.algorithms_available}")
        self.hasher = hashlib.new(self._algorithm_name)
        
    def hash(self, data: str) -> str:
        """
        Calcola l'hash della stringa data.

        Args:
            data: La stringa da hashare.

        Returns:
            L'hash della stringa in formato esadecimale.
        """
        self.hasher = hashlib.new(self._algorithm_name)
        self.hasher.update(data.encode('utf-8'))
        return self.hasher.hexdigest()
    def get_algorithm_name(self) -> str:
        """
        Restituisce il nome dell'algoritmo di hash.

        Returns:
            Il nome dell'algoritmo.
        """
        return self._algorithm_name
    def save_on_json(self) -> dict:
        """
        Restituisce una rappresentazione JSON dell'algoritmo, includendo il suo nome.
        """
        return {
            "class": "Generic_Hash_Algorithm",
            "algorithm_name": self._algorithm_name
        }
    @staticmethod
    def load_from_json(data: dict) -> 'Generic_Hash_Algorithm':
        """
        Carica un algoritmo di hash da una rappresentazione JSON.

        Args:
            data: Il dizionario contenente i dati dell'algoritmo.

        Returns:
            Un'istanza di GenericHashAlgorithm.
        """
        algorithm_name = data.get("algorithm_name")
        if not algorithm_name:
            raise ValueError("Dati JSON non validi: 'algorithm_name' mancante.")
        return Generic_Hash_Algorithm(algorithm_name)

    