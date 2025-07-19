import hashlib
import hmac
import secrets
from communication.Key import Key
from communication.Symmetric_Scheme import Symmetric_Scheme
from communication.Message import Message
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from constants import IV_SIZE, MAC_SIZE, SYMMETRIC_KEY_LENGTH
from cryptography.hazmat.primitives import padding, hashes, hmac as crypto_hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
class Cipher_Block_Chaining(Symmetric_Scheme):
    """
        Classe che implementa lo schema di crittografia Fernet.
        Utilizza la libreria cryptography per crittografare e decrittografare i messaggi.
        ! Deprecata, è stata sostituita da Parametric_Symmetric_Scheme come caso di default
    """

    def __init__(self, key:Key|None = None, IV:bytes|None = None):
        """
            Inizializza lo schema di crittografia Fernet con una chiave.
            Se la chiave non è fornita, ne genera una nuova.
        """

        if key is None:
            key = Key(secrets.token_bytes(SYMMETRIC_KEY_LENGTH))
        self._key = key

        if IV is None:
            IV = secrets.token_bytes(IV_SIZE)
        self._IV = IV

        super().__init__(key)
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=SYMMETRIC_KEY_LENGTH,
            salt=None,
            info=b'',
        )
        derived_keys = hkdf.derive(self._key.get_key())
        self._encryption_key = derived_keys[:SYMMETRIC_KEY_LENGTH]
        self._auth_key = derived_keys[SYMMETRIC_KEY_LENGTH:]
            
    def encrypt(self, message: Message) -> Message:
        """
            Metodo per crittografare un messaggio.
            Utilizza la chiave Fernet per crittografare il messaggio.
        """
        padder = padding.PKCS7(algorithms.AES.block_size).padder() # type: ignore
        padded_data = padder.update(message.get_content().encode('utf-8')) + padder.finalize()
        cipher = Cipher(algorithms.AES(self._encryption_key), modes.CBC(self._IV))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        data_to_authenticate = self._IV + ciphertext
        mac = hmac.new(self._auth_key, data_to_authenticate, hashlib.sha256).digest()
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
        ciphertext = data[IV_SIZE:-MAC_SIZE]
        cipher = Cipher(algorithms.AES(self._encryption_key), modes.CBC(data[:IV_SIZE]))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder() # type: ignore
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return Message(plaintext.decode('utf-8'))

    def sign(self, message: Message) -> Message:
        """
            Metodo per applicare le proprietà di autenticità e integrità al messaggio.
            In questo caso, la firma è semplicemente la crittografia del messaggio.
        """
        content_bytes = message.get_content().encode('utf-8')
        mac = hmac.new(self._auth_key, content_bytes, hashlib.sha256).digest().hex()
        return Message(message.get_content(),signature=mac)
        
        
        
    def verify(self, message: Message) -> bool:
        """
            Metodo per verificare l'autenticità e integrità di un messaggio.
            In questo caso, la verifica è semplicemente la decrittografia del messaggio.
        """
        try: 
            payload = bytes.fromhex(message.get_content())
            if len (payload) < IV_SIZE + MAC_SIZE:
                return False
            mac_to_verify = payload[-MAC_SIZE:]
            cipher = payload[IV_SIZE:-MAC_SIZE]
            data_to_authenticate = payload[:IV_SIZE] + cipher
            h = hmac.new(self._auth_key, data_to_authenticate, hashlib.sha256)
            return hmac.compare_digest(h.digest(), mac_to_verify)
        except ValueError:
            return False

    def save_on_json(self) -> dict:
        data = super().save_on_json()
        data['IV'] = self._IV.hex()
        data['scheme_type'] = "Cipher_Block_Chaining"
        return data
    
    @staticmethod
    def load_from_json(data: dict) -> 'Cipher_Block_Chaining':
        key = Key.load_from_json(data["key"])
        IV = bytes.fromhex(data["IV"])
        return Cipher_Block_Chaining(key, IV)