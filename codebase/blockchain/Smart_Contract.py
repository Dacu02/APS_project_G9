from blockchain.Blockchain import Blockchain
from communication.User import User


class Smart_Contract(User):
    def __init__(self, blockchain:Blockchain) -> None:
        self._blockchain = blockchain
