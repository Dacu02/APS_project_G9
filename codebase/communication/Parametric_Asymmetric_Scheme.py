from constants import ASYMMETRIC_KEY_LENGTH
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from communication.Message import Message
from communication.Key import Key

class Parametric_Asymmetric_Scheme(Asymmetric_Scheme):
    """
    Classe che implementa uno schema di crittografia asimmetrica basato su RSA.
    È parametrica per consentire la configurazione di algoritmi di hash,
    padding e parametri della chiave. Estende la classe Asymmetric_Scheme.
    """

    def __init__(
        self,
        private_key: Key | None = None,
        public_key: Key | None = None,
        key_size: int = ASYMMETRIC_KEY_LENGTH * 8,
        public_exponent: int = 65537,
        hash_algorithm_class=hashes.SHA256,
        encryption_padding_class=padding.OAEP,
        signing_padding_class=padding.PSS,
        only_public: bool = False
    ):
        """
        Inizializza lo schema RSA.
        - Se non vengono fornite chiavi, ne genera una nuova coppia.
        - I parametri crittografici possono essere personalizzati.
        """
        
        self._key_size = key_size
        self._public_exponent = public_exponent
        self._hash_algorithm_class = hash_algorithm_class
        self._encryption_padding_class = encryption_padding_class
        self._signing_padding_class = signing_padding_class

        
        self._hash_algorithm = self._hash_algorithm_class()

        
        self._encryption_padding = self._encryption_padding_class(
            mgf=padding.MGF1(algorithm=self._hash_algorithm),
            algorithm=self._hash_algorithm,
            label=None
        )
        self._signing_padding = self._signing_padding_class(
            mgf=padding.MGF1(self._hash_algorithm),
            salt_length=padding.PSS.MAX_LENGTH
        )

       
        self._rsa_private_key: rsa.RSAPrivateKey | None = None
        self._rsa_public_key: rsa.RSAPublicKey | None = None

        self._only_public = only_public
        self._private_key = private_key if not only_public else None
        
        super().__init__(private_key, public_key)
        self._only_public = only_public

        if self._private_key is not None and not only_public:
            try:
                self._rsa_private_key = serialization.load_pem_private_key(private_key.get_key(), password=None)
                self._rsa_public_key = self._rsa_private_key.public_key()
                if self._public_key is None:
                    self._public_key = Key(self._rsa_public_key.public_bytes(
                        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
            except Exception as e:
                raise ValueError(f"Failed to load private key from Key object: {e}") from e
        elif self._public_key is not None:
            try:
                self._rsa_public_key = serialization.load_pem_public_key(self._public_key.get_key())
            except Exception as e:
                raise ValueError(f"Failed to load public key from Key object: {e}") from e
        else:
            self._rsa_private_key = rsa.generate_private_key(
                public_exponent=self._public_exponent,
                key_size=self._key_size
            ) if not only_public else None
            self._rsa_public_key = self._rsa_private_key.public_key()

            self._private_key = Key(self._rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )) if not only_public else None
            self._public_key = Key(self._rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))


    def encrypt(self, message: Message) -> Message:
        if self._rsa_public_key is None:
            raise ValueError("Encryption failed: RSA public key is not initialized.")
        ciphertext = self._rsa_public_key.encrypt(
                message.get_content().encode('utf-8'),
                self._encryption_padding
            )
        return Message(ciphertext.hex(), signature=None)
    def decrypt(self, message: Message) -> Message:
        if self._rsa_private_key is None:
            raise ValueError("Decryption failed: RSA private key is not initialized.")
        try:
            ciphertext_bytes = bytes.fromhex(message.get_content())
            plaintext = self._rsa_private_key.decrypt(
                ciphertext_bytes,
                self._encryption_padding
            )
            return Message(plaintext.decode('utf-8'), signature=message.get_signature())
        except (ValueError, InvalidSignature) as e:
            raise ValueError(f"Decryption failed: Ciphertext invalid, key mismatch, or padding error. Original error: {e}") from e
        except Exception as e:
            raise ValueError(f"An unexpected error occurred during decryption: {e}") from e
    
    def sign(self, message: Message) -> Message:
        if self._rsa_private_key is None:
            raise ValueError("Signing failed: RSA private key is not initialized.")
        try:
            signature = self._rsa_private_key.sign(
                message.get_content().encode('utf-8'),
                self._signing_padding,
                self._hash_algorithm
            )
            return Message(message.get_content(), signature=signature.hex())
        except Exception as e:
            raise ValueError(f"Signing process failed: {e}") from e

    def verify(self, message: Message) -> bool:
        if self._rsa_public_key is None:
            return False
        if message.get_signature() is None:
            return False
        try:
            self._rsa_public_key.verify(
                bytes.fromhex(message.get_signature()),
                message.get_content().encode('utf-8'),
                self._signing_padding,
                self._hash_algorithm
            )
            return True
        except (InvalidSignature, ValueError):
            return False
        except Exception:
            return False

    def share_public_key(self) -> 'Parametric_Asymmetric_Scheme':
        if self._public_key is None:
            raise ValueError("Public Key (Key object) is not set and cannot be shared.")
        return Parametric_Asymmetric_Scheme(
            public_key=self._public_key,
            key_size=self._key_size,
            public_exponent=self._public_exponent,
            hash_algorithm_class=self._hash_algorithm_class,
            encryption_padding_class=self._encryption_padding_class,
            signing_padding_class=self._signing_padding_class,
            only_public=True
        )

    @staticmethod
    def load_from_json(data: dict) -> 'Parametric_Asymmetric_Scheme':


        only_public = "private_key" not in data or data["private_key"] is None

        private_key = Key.load_from_json(data["private_key"]) if not only_public else None
        public_key = Key.load_from_json(data["public_key"])

        key_size = data.get("key_size", 2048)
        public_exponent = data.get("public_exponent", 65537)
        hash_name = data.get("hash_algorithm", "SHA256")
        enc_padding_name = data.get("encryption_padding", "OAEP")
        sign_padding_name = data.get("signing_padding", "PSS")
        
        
        hash_class = getattr(hashes, hash_name)
        enc_padding_class = getattr(padding, enc_padding_name)
        sign_padding_class = getattr(padding, sign_padding_name)

        return Parametric_Asymmetric_Scheme(
            private_key=private_key,
            public_key=public_key,
            key_size=key_size,
            public_exponent=public_exponent,
            hash_algorithm_class=hash_class,
            encryption_padding_class=enc_padding_class,
            signing_padding_class=sign_padding_class,
            only_public=only_public
        )

    def save_on_json(self) -> dict:
        data = super().save_on_json()
        data["scheme_type"] = "Parametric_Asymmetric_Scheme"
        if self._only_public:
            del data["private_key"] # A solo scopo estetico
        data["key_size"] = self._key_size
        data["public_exponent"] = self._public_exponent
        data["hash_algorithm"] = self._hash_algorithm_class.__name__
        data["encryption_padding"] = self._encryption_padding_class.__name__
        data["signing_padding"] = self._signing_padding_class.__name__
        return data