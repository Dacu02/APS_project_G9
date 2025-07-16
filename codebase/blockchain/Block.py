# Tutto il codice è generato 

class Block():
    def __init__(self, index: int, previous_hash: str, timestamp: float, data: dict):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
            Calcola l'hash del blocco.
        """
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __str__(self) -> str:
        return f"Block(Index: {self.index}, Previous Hash: {self.previous_hash}, Timestamp: {self.timestamp}, Data: {self.data}, Hash: {self.hash})"
    def save_on_json(self) -> dict:
        """
            Restituisce una rappresentazione JSON del blocco.
        """
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "hash": self.hash
        }
    
    @staticmethod
    def load_from_json(data: dict) -> 'Block':
        """
            Carica un blocco da una rappresentazione JSON.
        """
        return Block(
            index=data["index"],
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
            data=data["data"]
        )
    
    