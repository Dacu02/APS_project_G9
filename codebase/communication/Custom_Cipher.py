
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from communication.Message import Message
from communication.Key import Key


class Custom_Cipher(Asymmetric_Scheme):
    """
        Classe che rappresenta un cifrario personalizzato, estende la classe Asymmetric_Scheme.
        Implementa i metodi per crittografare e decrittografare i messaggi utilizzando un algoritmo di cifratura personalizzato.
    """

    def __init__(self, private_key: Key | None = None, public_key: Key | None = None):
        if private_key is None:
            rsa_private = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self._private_key = rsa_private
            self._public_key = Key(rsa_private.public_key())
        else:
            self._private_key = private_key
            self._public_key = public_key or Key(private_key.get_private().public_key())

        super().__init__(self._private_key, self._public_key)

    def encrypt(self, message: Message) -> Message:
        public_key = serialization
        ciphertext = public_key.encrypt(
            message.get_content().encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return Message(ciphertext, signature=None)
    def decrypt(self, message: Message) -> Message:
        private_key = serialization.load_pem_private_key(
            self._private_key.get_private().private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL
            ),
            password=None
        )
        plaintext = private_key.decrypt(
            message.get_content(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return Message(plaintext.decode('utf-8'), signature=None)

    def sign(self, message: Message) -> Message:
        signature = self._private_key.get_private().sign(
            message.get_content().encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return Message(message.get_content(), signature=signature)

    def verify(self, message: Message) -> bool:
        try:
            self._public_key.get_public().verify(
                message.get_signature(),
                message.get_content().encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
        

    def share_public_key(self) -> 'Custom_Cipher':
        """
        Restituisce un nuovo cifrario con solo la chiave pubblica.
        """
        return Custom_Cipher(public_key=self._public_key)

    @staticmethod
    def load_from_json(data: dict) -> 'Custom_Cipher':
        private_key = Key.load_from_json(data["private_key"])
        public_key = Key.load_from_json(data["public_key"])
        return Custom_Cipher(private_key, public_key)

    def save_on_json(self) -> dict:
        return {
            #"private_key": self._private_key.save_on_json(),
            #"public_key": self._public_key.save_on_json(),
            "type": "Custom_Cipher"
        }
