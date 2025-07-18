import json
from typing import TypedDict
from communication.Key import Key
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from communication.Message import Message

class CertificateContent(TypedDict):
    key: dict
    timestamp: str


class Certificate(Message):
    def __init__(self, content: CertificateContent, scheme: Asymmetric_Scheme):
        """
            Classe che rappresenta un certificato, estende la classe Message.
            Contiene il contenuto del certificato e una firma obbligatoria.
        """
        super().__init__(json.dumps(content))
        signed = scheme.sign(self)
        if not isinstance(signed, Message):
            raise TypeError(f"Il certificato deve essere un'istanza di Message, ma è di tipo {type(signed)}")

        self._signature = signed.get_signature()

    def verify_signature(self, public_key: Asymmetric_Scheme) -> bool:
        return public_key.verify(self)
    
    def read_key(self) -> Asymmetric_Scheme:
        """
            Restituisce la chiave pubblica contenuta nel certificato.
        """
        content = json.loads(self.get_content())
        return Asymmetric_Scheme.load_from_json(content["key"])
    
    def read_timestamp(self) -> str:
        """
            Restituisce il timestamp del certificato.
        """
        content = json.loads(self.get_content())
        return content["timestamp"]
    
    def save_on_json(self) -> dict:
        """
            Restituisce una rappresentazione JSON del certificato.
        """
        return {
            "content": json.loads(self._content),
            "signature": self._signature
        }
    
    @staticmethod
    def load_from_json(data: dict) -> 'Certificate':
        """
            Carica un certificato da una rappresentazione JSON.
        """
        content = data["content"]
        signature = data["signature"]
        scheme = Asymmetric_Scheme.load_from_json(content["key"])
        cert = Certificate(content, scheme)
        cert._signature = signature
        return cert