from blockchain.Block import Block


class Blockchain():
    """
        Classe che rappresenta una blockchain.
    """

    def __init__(self):
        """
            Inizializza una blockchain vuota.
        """

        self._blocks: list[Block] = []

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