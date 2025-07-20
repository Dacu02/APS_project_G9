from cycler import V
from communication.Hash_Algorithm import Hash_Algorithm
from constants import BLOCKCHAIN_HASH_ALGORITHM


class MerkleTree():
    class _Node():
        def __init__(self, hash:str|None=None, left=None, right=None):
            self._hash = hash
            self._left:MerkleTree._Node|None = left
            self._right:MerkleTree._Node|None = right

        def __len__(self) -> int:
            """
                Restituisce il numero di nodi nel Merkle Tree.
                Il numero di nodi è dato dal numero di foglie - 1, poiché l'albero è completo.
            """
            left = self.get_left()
            right = self.get_right()
            if left is None or right is None:
                return 1
            else:
                return 1 + len(left) + len(right)

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

        def _validate(self, hash_alg:Hash_Algorithm) -> bool:
            
            if not self.get_hash():
                return False
            
            hash_function = hash_alg.hash
            left = self.get_left()
            right = self.get_right()

            if left and right:
                left_hash = left.get_hash()
                right_hash = right.get_hash()
                if left_hash is None or right_hash is None:
                    return False
                return (hash_function(left_hash + right_hash) == self.get_hash()) and left._validate(hash_alg) and right._validate(hash_alg)
            elif not left and not right:
                return self.get_hash() is not None
            else:
                return False

        def _validate_leaf(self, hash_leaf:str):
            """
                Controlla se il nodo corrente è una foglia e se il suo hash corrisponde a quello della foglia specificata.
            """
            left_node = self.get_left()
            right_node = self.get_right()
            if not left_node and not right_node:
                return self.get_hash() == hash_leaf
            elif left_node and right_node:
                return left_node._validate_leaf(hash_leaf) or right_node._validate_leaf(hash_leaf)
            raise ValueError("Il nodo non è una foglia né è intero e l'albero non è valido")

    def __init__(self, leaves: list[str], hash_algorithm: Hash_Algorithm = BLOCKCHAIN_HASH_ALGORITHM()):
        """
            Inizializza un Merkle Tree con i nodi foglia specificati.
        """
        self._hash = hash_algorithm
        if not leaves:
            return
        merkle_leaves: list[MerkleTree._Node] = [MerkleTree._Node(leaf) for leaf in leaves]
        self._root = self._build_tree(merkle_leaves)
        # print(len(self))

    def __len__(self) -> int:
        """
            Restituisce il numero di nodi nel Merkle Tree.
            Il numero di nodi è dato dal numero di foglie - 1, poiché l'albero è completo.
        """
        left = self._root.get_left()
        right = self._root.get_right()
        if not left or not right:
            return 1
        else:
            return 1 + len(left) + len(right)

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
        node.set_hash(self._hash.hash(left_hash + right_hash))
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
    
    def get_root(self) -> _Node | None:
        return self._root
    
    def validate(self) -> bool:
        """
            Controlla che il Merkle Tree sia valido.
            Un Merkle Tree è valido se la radice ha un hash e tutti i nodi hanno figli validi.
        """
        if not self._root or not self._root.get_hash():
            return False

        return self._root._validate(self._hash)

    def validate_leafs(self, leafs: list[str]) -> bool:
        """
            Controlla che le foglie specificate siano valide nel Merkle Tree.
            Parametri:
            - leafs: lista di stringhe che rappresentano le foglie, hashate, da verificare se appartengono tutte all'albero
        """
        if not leafs:
            return False
        
        root = self.get_root()
        if not root or not root.get_hash():
            raise ValueError("Il Merkle Tree non è valido o non ha una radice.")
        
        for leaf in leafs:
            if not root._validate_leaf(leaf):
                return False
        return True
