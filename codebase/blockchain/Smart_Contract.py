from blockchain.Blockchain import Blockchain
from blockchain.Block import Block
from blockchain.MerkleTree import MerkleTree
from communication.Asymmetric_Scheme import Asymmetric_Scheme
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
    
    def certificate_credential_MerkleTree(self, tree:MerkleTree, author_public_key:Asymmetric_Scheme) -> str:
        """
            Certifica un Merkle Tree, restituendo il suo ID.
            Il Merkle Tree deve essere già stato costruito con i dati della credenziale.
        """
        if not tree or not tree.get_root():
            raise ValueError("Il Merkle Tree non è stato costruito correttamente.")
        
        if not isinstance(tree, MerkleTree):
            raise TypeError("Il parametro 'tree' deve essere un'istanza di MerkleTree.")

        root = tree.get_root()
        if not root or not root.get_hash():
            raise ValueError("Il Merkle Tree non ha un hash valido nella radice.")

        if not self._validate_merkle_tree(tree):
            raise ValueError("Il Merkle Tree non è valido.")
        
        last_block = self._blockchain.get_last_block()
        if not last_block:
            prev_ID = self._hashing.hash("Genesis Block")
        else:
            prev_ID = last_block.get_ID()
        key = author_public_key.get_public_key()
        if not key:
            raise ValueError("La chiave pubblica dell'autore non è valida.")
        block = Block(
            prev_ID=prev_ID,
            author=self._hashing.hash(key.get_key().hex()),
            merkle_or_ID=tree,
            delete_flag=False
        )
        self._add_block(block)
        return block.get_ID()

    def _validate_merkle_tree(self, tree:MerkleTree) -> bool:
        """
            Controlla che il Merkle Tree sia valido.
        """
        return tree.validate()