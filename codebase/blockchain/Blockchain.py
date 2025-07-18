from blockchain.Block import Block
from communication.Hash_Algorithm import Hash_Algorithm
from constants import BLOCKCHAIN_HASH_ALGORITHM


class Blockchain():
    """
        Classe che rappresenta una blockchain.
    """

    def __init__(self, hash_algorithm:Hash_Algorithm=BLOCKCHAIN_HASH_ALGORITHM()):
        """
            Inizializza una blockchain vuota.
        """

        self._blocks: list[Block] = []
        self._hashing = hash_algorithm

    def add_block(self, block: Block) -> None:
        """
            Aggiunge un blocco alla blockchain.
        """
        if not isinstance(block, Block):
            raise TypeError("Il blocco deve essere un'istanza della classe Block.")
        
        if self._blocks and block.get_prev_ID() != self._blocks[-1].get_ID():
            raise ValueError("Il blocco non è collegato correttamente alla blockchain.")
        
        self._blocks.append(block)

    def get_blocks(self) -> list[Block]:
        """
            Restituisce la lista dei blocchi nella blockchain.
        """
        return self._blocks
    
    def get_last_block(self) -> Block | None:
        """
            Restituisce l'ultimo blocco della blockchain, o None se la blockchain è vuota.
        """
        if not self._blocks:
            return None
        return self._blocks[-1]

    def is_valid(self) -> bool:
        """
            Verifica la validità della blockchain.
            Controlla che ogni blocco sia collegato correttamente al blocco precedente.
        """
        if not self._blocks:
            return True
        
        for i in range(1, len(self._blocks)):
            if self._blocks[i].get_prev_ID() != self._blocks[i-1].get_ID():
                return False
        
        return True
    
    def find_block(self, ID:str) -> Block|None:
        """
            Trova un blocco nella blockchain per ID.
            Restituisce il blocco se trovato, altrimenti None.
        """
        for block in self._blocks:
            if block.get_ID() == ID:
                return block
            
        return None

    def save_on_json(self) -> list[dict]:
        """
            Salva la blockchain in formato JSON.
        """
        return [block.save_on_json() for block in self._blocks]

    @staticmethod
    def load_from_json(data: list[dict]) -> 'Blockchain':
        blockchain = Blockchain()
        for block_data in data:
            block = Block.load_from_json(block_data)
            blockchain.add_block(block)
        return blockchain
    
    def get_hashing_algorithm(self) -> Hash_Algorithm:
        """
            Restituisce l'algoritmo di hashing utilizzato dalla blockchain.
        """
        return self._hashing
    
    def next(self, block:Block) -> Block|None:
        """
            Restituisce il blocco successivo nella blockchain.
            Se non esiste, restituisce None.
        """
        if not self._blocks:
            return None
        
        for i in range(len(self._blocks) - 1):
            if self._blocks[i] == block:
                return self._blocks[i + 1]
        
        return None