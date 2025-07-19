from blockchain.Blockchain import Blockchain
from blockchain.Block import Block
from blockchain.MerkleTree import MerkleTree
from actors.University import University
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from communication.User import User
from constants import BLACKLIST_THRESHOLD

class Smart_Contract(User):
    def __init__(self, blockchain:Blockchain, scheme:Asymmetric_Scheme, blacklist: dict[str, list[Asymmetric_Scheme]]|None) -> None:
        super().__init__("SMART_CONTRACT")
        self._blockchain = blockchain
        self._hashing = self._blockchain.get_hashing_algorithm()
        self._keys[self._code] = scheme
        if not blacklist:
            self._blacklist = {}
        else:
            self._blacklist = blacklist

    def _link_blockchain(self, blockchain: Blockchain) -> None:
        """
            Collega lo smart contract alla blockchain.
        """
        self._blockchain = blockchain

    def whitelist_university(self, university:University, author_public_key: Asymmetric_Scheme) -> None:
        """
            Aggiunge un'università alla whitelist dello smart contract.
            Restituisce l'ID del blocco creato.
        """
        self._keys[university.get_code()] = author_public_key

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
    
    def certificate_credential_MerkleTree(self, tree:MerkleTree, university:University) -> str:
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
        key = self._keys.get(university.get_code())
        if not key:
            raise ValueError("La chiave pubblica dell'autore non è valida.")
        if not isinstance(key, Asymmetric_Scheme):
            raise TypeError("La chiave pubblica dell'autore deve essere un'istanza di Asymmetric_Scheme.")
        key = key.get_public_key()
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

    def save_on_json(self) -> dict:
        data = super().save_on_json()
        data["keys"] = {k: v.save_on_json() for k, v in self._keys.items()}
        data["blockchain"] = [block.save_on_json() for block in self._blockchain.get_blocks()]
        data["blacklist"] = {uni_code: [voter.save_on_json() for voter in voter_list] for uni_code, voter_list in self._blacklist.items()}
        return data

    @staticmethod
    def load_from_json(data: dict) -> 'Smart_Contract':
        """
            Carica lo smart contract da un dizionario JSON.
        """
        scheme = Asymmetric_Scheme.load_from_json(data.get("keys", {}).get("SMART_CONTRACT", {}))
        blockchain = Blockchain.load_from_json(data.get("blockchain", []))
        blacklist = {uni_code: [Asymmetric_Scheme.load_from_json(voter) for voter in voter_list] for uni_code, voter_list in data.get("blacklist", {}).items()}
        return Smart_Contract(blockchain, scheme, blacklist)


    def vote_blacklist(self, voter: Asymmetric_Scheme, to_blacklist: University) -> None:
        """
            Vota per aggiungere un'università alla blacklist.
        """
        if not self._blacklist[to_blacklist.get_code()]:
            self._blacklist[to_blacklist.get_code()] = [voter]
        else:
            if voter not in self._blacklist[to_blacklist.get_code()]:
                self._blacklist[to_blacklist.get_code()].append(voter)

    def is_blacklisted(self, university: University) -> bool:
        """
            Controlla se un'università è nella blacklist.
        """
        return university.get_code() in self._blacklist and len(self._blacklist[university.get_code()]) > len(self._keys) // BLACKLIST_THRESHOLD

    def validate_credential_MerkleTreeLeafs(self, leafs: list[str], credential_ID: str) -> bool:
        """
            Valida le foglie di un Merkle Tree per una determinata credenziale.
        """
        if not leafs or not credential_ID:
            raise ValueError("Le foglie e l'ID della credenziale non possono essere vuoti.")

        # Ottiene il blocco dov'è contenuto il Merkle Tree della credenziale
        block = self._blockchain.find_block(credential_ID)
        if not block:
            return False

        # Controlla se il Merkle Tree è valido
        merkle_tree = block.get_merkle_or_ID()
        if not isinstance(merkle_tree, MerkleTree):
            raise TypeError("Il Merkle Tree non è valido o non è un'istanza di MerkleTree.")

        if not merkle_tree.validate_leafs(leafs):
            return False

        # Controlla se l'ID è stato revocato successivamente nella blockchain
        next_block = self._blockchain.next(block)
        while next_block:
            if next_block.get_delete_flag() and next_block.get_merkle_or_ID() == credential_ID:
                return False #Il blocco ha revocato la credenziale

            next_block = self._blockchain.next(next_block)

        return True