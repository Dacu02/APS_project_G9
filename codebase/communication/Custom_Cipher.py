
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
        

        self._rsa_private_key: rsa.RSAPrivateKey | None = None
        self._rsa_public_key: rsa.RSAPublicKey | None = None

        if private_key is not None:
            try:
                self._rsa_private_key = serialization.load_pem_private_key(private_key.get_key(), password=None)
                self._rsa_public_key = self._rsa_private_key.public_key()
                if self._public_key is None:
                    self._public_key = Key(self._rsa_public_key.public_bytes(
                        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
            except Exception as e:
                print(f"Error loading private key: {e}")
                raise ValueError(f"Failed to load private key from Key object: {e}") from e
        elif public_key is not None:
            try:
                self._rsa_public_key = serialization.load_pem_public_key(public_key.get_key())
            except Exception as e:
                print(f"Error loading public key: {e}")
                raise ValueError(f"Failed to load public key from Key object: {e}") from e
        else:
            self._rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self._rsa_public_key = self._rsa_private_key.public_key()

            self._private_key = Key(self._rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            self._public_key = Key(self._rsa_public_key.public_bytes(
                encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        super().__init__(private_key, public_key)

    def encrypt(self, message: Message) -> Message:
        ciphertext = self._rsa_public_key.encrypt(
                message.get_content().encode('utf-8'),
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        return Message(ciphertext.hex(), signature=None)

    def decrypt(self, message: Message) -> Message:
        try:
            ciphertext_bytes = bytes.fromhex(message.get_content())
            plaintext = self._rsa_private_key.decrypt(
                ciphertext_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return Message(plaintext.decode('utf-8'), signature=message.get_signature())
        except (ValueError, InvalidSignature) as e:
            raise ValueError(f"Decryption failed: Ciphertext invalid, key mismatch, or padding error. Original error: {e}") from e
        except Exception as e:
            raise ValueError(f"An unexpected error occurred during decryption: {e}") from e

    def sign(self, message: Message) -> Message:
        if self._rsa_private_key is None:
            raise ValueError("Signing failed: RSA private key object is not initialized.")
        try:
            signature = self._rsa_private_key.sign(
                message.get_content().encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return Message(message.get_content(), signature=signature.hex())
        except Exception as e:
            raise ValueError(f"Signing process failed: {e}") from e

    def verify(self, message: Message) -> bool:
        if self._rsa_public_key is None:
            print("Verification failed: RSA public key object is not initialized.") # For debugging
            return False
        if message.get_signature() is None:
            print("Verification failed: Message has no signature to verify.") # For debugging
            return False
        try:
            self._rsa_public_key.verify(
                bytes.fromhex(message.get_signature()),
                message.get_content().encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except (InvalidSignature, ValueError) as e:
            print(f"Verification failed: Signature invalid or content mismatch. Error: {e}") # For debugging
            return False
        except Exception as e:
            print(f"An unexpected error occurred during verification: {e}") # For debugging
            return False

    def share_public_key(self) -> 'Custom_Cipher':
        """
        Restituisce un nuovo cifrario con solo la chiave pubblica.
        """
        if self._public_key is None:
            raise ValueError("Public Key (Key object) is not set and cannot be shared.")
        return Custom_Cipher(public_key=self._public_key)

    @staticmethod
    def load_from_json(data: dict) -> 'Custom_Cipher':
        priv_k_data = data.get("private_key")
        pub_k_data = data.get("public_key")

        private_key = Key.load_from_json(priv_k_data) if priv_k_data else None
        public_key = Key.load_from_json(pub_k_data) if pub_k_data else None

        return Custom_Cipher(private_key, public_key)

    def save_on_json(self) -> dict:
        data = super().save_on_json()
        data["scheme_type"] = "Custom_Cipher"
        return data