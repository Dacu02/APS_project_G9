from blockchain.MerkleTree import MerkleTree


class Block():
    """
    Classe che rappresenta un blocco nella blockchain.
    """
    def __init__(self, prev_ID: str, author:str, merkle_or_ID:MerkleTree|str, delete_flag:bool=False):
        self._prev_ID = prev_ID
        self._author = author
        self._delete_flag = delete_flag
        self._merkle_or_ID = merkle_or_ID
        self._ID = hash((self._prev_ID, self._author, self._merkle_or_ID, self._delete_flag)) #TODO Definisci il metodo di hash

    def get_prev_ID(self) -> str:
        return self._prev_ID

    def get_author(self) -> str:
        return self._author

    def get_delete_flag(self) -> bool:
        return self._delete_flag

    def get_merkle_or_ID(self) -> MerkleTree | str:
        return self._merkle_or_ID

    def get_ID(self) -> int:
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
        block = Block(
            prev_ID=data['prev_ID'],
            author=data['author'],
            merkle_or_ID=data['merkle_or_ID'],
            delete_flag=data['delete_flag']
        )
        block._ID = data['ID']
        return block