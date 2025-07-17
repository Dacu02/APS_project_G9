



class MerkleTree():
    class _Node():
        def __init__(self, hash:str|None=None, left=None, right=None):
            self._hash = hash
            self._left:MerkleTree._Node|None = left
            self._right:MerkleTree._Node|None = right

        def get_hash(self) -> str|None:
            return self._hash

        def set_hash(self, hash: str) -> None:
            self._hash = hash

        def get_left(self) -> 'MerkleTree._Node | None':
            return self._left

        def set_left(self, left: 'MerkleTree._Node | None'):
            self._left = left

        def get_right(self) -> 'MerkleTree._Node | None':
            return self._right

        def set_right(self, right: 'MerkleTree._Node | None'):
            self._right = right

    def __init__(self, leaves_hashes: list[str]):
        """
            Inizializza un Merkle Tree con i nodi foglia specificati.
        """
        if not leaves_hashes or len(leaves_hashes) == 0:
            return 
        leaves: list[MerkleTree._Node] = [MerkleTree._Node(leaf) for leaf in leaves_hashes]
        self._root: MerkleTree._Node | None = None
        self._root = self._build_tree(leaves)

    def _build_tree(self, leaves:list[_Node]) -> _Node:
        """
            Costruisce il MerkleTree a partire dalle foglie, siccome è un albero completo per definizione.
            Cerca di bilanciarlo quanto più possibile, per cui calcola a priori il numero di nodi necessario (NUM_FOGLIE-1).
        """
        if len(leaves) == 1:
            return leaves[0]            

        node = MerkleTree._Node()
        node.set_left(self._build_tree(leaves[:len(leaves)//2]))
        node.set_right(self._build_tree(leaves[len(leaves)//2:]))

        left_node = node.get_left()
        right_node = node.get_right()
        if left_node is None or right_node is None:
            raise ValueError("Il Merkle Tree deve essere completo e bilanciato.")
        
        left_hash = left_node.get_hash()
        right_hash = right_node.get_hash()
        if left_hash is None or right_hash is None:
            raise ValueError("I nodi figli devono avere un hash valido.")
        node.set_hash(left_hash + right_hash) #TODO Definisci il metodo di hash
        return node


    def _node_to_dict(self, node: 'MerkleTree._Node|None') -> dict:
        if node is None:
            return {}
        return {
            'hash': node.get_hash(),
            'left': self._node_to_dict(node.get_left()),
            'right': self._node_to_dict(node.get_right())
        }

    @staticmethod
    def _dict_to_node(data: dict) -> 'MerkleTree._Node|None':
        if not data:
            return None
        node = MerkleTree._Node(data['hash'])
        node.set_left(MerkleTree._dict_to_node(data['left']))
        node.set_right(MerkleTree._dict_to_node(data['right']))
        return node

    def save_on_json(self) -> dict:
        data = self._node_to_dict(self._root)
        return data

    @staticmethod
    def load_from_json(data: dict) -> 'MerkleTree':
        tree = MerkleTree([])
        tree._root = MerkleTree._dict_to_node(data)
        return tree