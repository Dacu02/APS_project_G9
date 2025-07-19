import hashlib
import hmac
import secrets
from communication.Key import Key
from communication.Symmetric_Scheme import Symmetric_Scheme
from communication.Message import Message
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf import hkdf

from constants import IV_SIZE, MAC_SIZE, SYMMETRIC_KEY_LENGTH
from cryptography.hazmat.primitives import padding, hashes, hmac as crypto_hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
class Parametric_Symmetric_Scheme(Symmetric_Scheme):
    """
        Classe che implementa lo schema di crittografia Fernet.
        Utilizza la libreria cryptography per crittografare e decrittografare i messaggi.
    """

    def __init__(
        self,
        key: Key | None = None,
        IV: bytes | None = None,
        cipher_algorithm=algorithms.AES,
        mode_class=modes.CBC,
        hash_algorithm=hashes.SHA256(),
        kdf_class=HKDF,
        padding_scheme=padding.PKCS7,
        mac_hash=hashlib.sha256,
        salt: bytes | None = None,
        kdf_info: bytes = b'',
        IV_size: int = IV_SIZE,
        MAC_size: int = MAC_SIZE,
        key_length: int = SYMMETRIC_KEY_LENGTH,
    ):

        """
            Inizializza lo schema di crittografia Fernet con una chiave.
            Se la chiave non è fornita, ne genera una nuova.
            Parametri (opzionali):
                - key: Chiave da utilizzare per la crittografia.
                - IV: Inizialization vector da utilizzare per la crittografia.
                - cipher_algorithm: Algoritmo di cifratura da utilizzare (default: AES).
                - mode_class: Modalità di cifratura da utilizzare (default: CBC).
                - hash_algorithm: Algoritmo di hash da utilizzare (default: SHA256).
                - kdf_class: Classe di derivazione della chiave da utilizzare (default: HKDF).
                - padding_scheme: Schema di padding da utilizzare (default: PKCS7).
                - mac_hash: Algoritmo di hash da utilizzare per il MAC (default: SHA256).
                - salt: Sale da utilizzare per la derivazione della chiave (default: None).
                - kdf_info: Informazioni da utilizzare per la derivazione della chiave (default: b'').
                - IV_size: Dimensione dell'IV (default: 16).
                - MAC_size: Dimensione del MAC (default: 32).
                - key_length: Lunghezza della chiave (default: 32).
        Raises:
            ValueError: Se la chiave non è valida o se l'IV non è della dimensione corretta.
            TypeError: Se i parametri forniti non sono del tipo corretto.

        """
        self._IV_size = IV_size
        self._MAC_size = MAC_size
        self._key_length = key_length

        if key is None:
            key = Key(secrets.token_bytes(self._key_length))
        self._key = key

        if IV is None:
            IV = secrets.token_bytes(self._IV_size)
        self._IV = IV
        
        self._cipher_algorithm = cipher_algorithm
        self._mode_class = mode_class
        self._hash_algorithm = hash_algorithm
        self._kdf_class = kdf_class
        self._padding_scheme = padding_scheme
        self._mac_hash = mac_hash
        self._salt = salt
        self._kdf_info = kdf_info

        super().__init__(key)

        hkdf = self._kdf_class(
            algorithm=self._hash_algorithm,
            length=2 * self._key_length,  # auth + encryption key
            salt=self._salt,
            info=self._kdf_info,
        )
            
        derived_keys = hkdf.derive(self._key.get_key())
        self._encryption_key = derived_keys[:self._key_length]
        self._auth_key = derived_keys[self._key_length:]

        

            
    def encrypt(self, message: Message) -> Message:
        """
            Metodo per crittografare un messaggio.
            Utilizza la chiave Fernet per crittografare il messaggio.
        """
        padder = self._padding_scheme(self._cipher_algorithm.block_size).padder() # type: ignore
        padded_data = padder.update(message.get_content().encode('utf-8')) + padder.finalize()
        cipher = Cipher(self._cipher_algorithm(self._encryption_key), self._mode_class(self._IV))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        data_to_authenticate = self._IV + ciphertext
        mac = hmac.new(self._auth_key, data_to_authenticate, self._mac_hash).digest()
        new_content = (self._IV + ciphertext + mac).hex()
        return Message(new_content,signature = None)


    def decrypt(self, message: Message) -> Message:
        """
            Metodo per decrittografare un messaggio.
            Utilizza la chiave Fernet per decrittografare il messaggio.
        """
        if not self.verify(message):
            raise ValueError("Il messaggio non è autentico o è stato manomesso.")
        data = bytes.fromhex(message.get_content())
        ciphertext = data[self._IV_size:-self._MAC_size]
        cipher = Cipher(self._cipher_algorithm(self._encryption_key), self._mode_class(data[:self._IV_size]))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = self._padding_scheme(self._cipher_algorithm.block_size).unpadder() # type: ignore
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return Message(plaintext.decode('utf-8'))

    def sign(self, message: Message) -> Message:
        """
            Metodo per applicare le proprietà di autenticità e integrità al messaggio.
            In questo caso, la firma è semplicemente la crittografia del messaggio.
        """
        content_bytes = message.get_content().encode('utf-8')
        mac = hmac.new(self._auth_key, content_bytes, self._mac_hash).digest().hex()
        return Message(message.get_content(),signature=mac)
        
        
        
    def verify(self, message: Message) -> bool:
        signature = message.get_signature()
        if signature:
            # Verifica la firma del contenuto
            expected_mac = hmac.new(self._auth_key, message.get_content().encode('utf-8'), self._mac_hash).digest().hex()
            return hmac.compare_digest(expected_mac, signature)
        else:
            return False



    def save_on_json(self) -> dict:
        data = super().save_on_json()
        data['scheme_type'] = "Parametric_Symmetric_Scheme"
        data['IV'] = self._IV.hex()
        data['IV_size'] = self._IV_size
        data['MAC_size'] = self._MAC_size
        data['key_length'] = self._key_length
        data['cipher_algorithm'] = self._cipher_algorithm.name
        data['mode_class'] = self._mode_class.name
        data['hash_algorithm'] = self._hash_algorithm.name
        data['kdf_class'] = self._kdf_class.__name__
        data['padding_scheme'] = self._padding_scheme.__name__
        return data
    
    @staticmethod
    def load_from_json(data: dict) -> 'Parametric_Symmetric_Scheme':
        key = Key.load_from_json(data["key"])
        IV = bytes.fromhex(data["IV"])
        cipher_algorithm = getattr(algorithms, data["cipher_algorithm"])
        mode_class = getattr(modes, data["mode_class"])
        hash_algorithm = getattr(hashes, data["hash_algorithm"].upper())()
        kdf_class = getattr(hkdf, data["kdf_class"])
        padding_scheme = getattr(padding, data["padding_scheme"])
        IV_size = data.get("IV_size", IV_SIZE)
        MAC_size = data.get("MAC_size", MAC_SIZE)
        key_length = data.get("key_length", SYMMETRIC_KEY_LENGTH)

        return Parametric_Symmetric_Scheme(
            key=key,
            IV=IV,
            cipher_algorithm=cipher_algorithm,
            mode_class=mode_class,
            hash_algorithm=hash_algorithm,
            kdf_class=kdf_class,
            padding_scheme=padding_scheme,
            IV_size=IV_size,
            MAC_size=MAC_size,
            key_length=key_length
        )
    