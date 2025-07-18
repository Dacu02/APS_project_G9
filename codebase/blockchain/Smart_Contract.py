from blockchain.Blockchain import Blockchain
from blockchain.Block import Block
from communication.User import User


class Smart_Contract(User):
    def __init__(self, blockchain:Blockchain) -> None:
        self._blockchain = blockchain
        self._hashing = self._blockchain.get_hashing_algorithm()

    def get_blockchain(self) -> Blockchain:
        """
            Restituisce la blockchain associata allo smart contract.
        """
        return self._blockchain
    
    def _add_block(self, block: Block) -> None:
        """
            Aggiunge un blocco alla blockchain.
        """
        self._blockchain.add_block(block)

    def _invalidate_block(self, block_ID:str) -> bool:
        """
            Invalida un blocco già presente sulla blockchain.
        """
        top_block = self._blockchain.get_last_block()
        if not top_block:
            return False
        block_to_invalidate = self._blockchain.find_block(block_ID)
        if not block_to_invalidate:
            return False
        
        new_block = Block(
            prev_ID=top_block.get_ID(),
            author=block_to_invalidate.get_author(),
            merkle_or_ID=block_to_invalidate.get_ID(),
            delete_flag=True
        ) 
        self._blockchain.add_block(new_block)
        return True
    
    
