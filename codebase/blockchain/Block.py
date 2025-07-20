from blockchain.MerkleTree import MerkleTree
from communication.Hash_Algorithm import Hash_Algorithm
from constants import BLOCKCHAIN_HASH_ALGORITHM


class Block():
    """
    Classe che rappresenta un blocco nella blockchain.
    """
    def __init__(self, prev_ID: str, author:str, merkle_or_ID:MerkleTree|str, delete_flag:bool=False, hashing_algorithm:Hash_Algorithm = BLOCKCHAIN_HASH_ALGORITHM()):
        self._prev_ID = prev_ID
        self._author = author
        self._delete_flag = delete_flag
        self._merkle_or_ID = merkle_or_ID
        
        if isinstance(merkle_or_ID, MerkleTree):
            root = merkle_or_ID.get_root()
            if root:
                string_merkle = root.get_hash()
                if not string_merkle:
                    raise ValueError("Hash della radice del Merkle Tree non valido")
            else:
                string_merkle = ""
        else:
            string_merkle = merkle_or_ID
        self._ID = hashing_algorithm.hash(self._prev_ID + self._author + string_merkle + str(self._delete_flag))

    def get_prev_ID(self) -> str:
        return self._prev_ID

    def get_author(self) -> str:
        return self._author

    def get_delete_flag(self) -> bool:
        return self._delete_flag

    def get_merkle_or_ID(self) -> MerkleTree | str:
        return self._merkle_or_ID

    def get_ID(self) -> str:
        return self._ID

    def save_on_json(self) -> dict:
        return {
            'prev_ID': self._prev_ID,
            'author': self._author,
            'delete_flag': self._delete_flag,
            'merkle_or_ID': self._merkle_or_ID if isinstance(self._merkle_or_ID, str) else self._merkle_or_ID.save_on_json(),
            'ID': self._ID
        }
    
    @staticmethod
    def load_from_json(data: dict) -> 'Block':

        if data['delete_flag']:
            merkle_or_ID = data['merkle_or_ID']
        else:
            merkle_or_ID = MerkleTree.load_from_json(data['merkle_or_ID'])

        block = Block(
            prev_ID=data['prev_ID'],
            author=data['author'],
            merkle_or_ID=merkle_or_ID,
            delete_flag=data['delete_flag']
        )
        block._ID = data['ID']
        return block