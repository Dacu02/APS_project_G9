import hashlib
import hmac
from codebase.communication.Key import Key
from communication.Symmetric_Scheme import Symmetric_Scheme
from communication.Message import Message
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import constants as c
import os 
from cryptography.hazmat.primitives import padding,hashes,hmac
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
class Custom_Cipher(Symmetric_Scheme):
    """
        Classe che implementa lo schema di crittografia Fernet.
        Utilizza la libreria cryptography per crittografare e decrittografare i messaggi.
    """

    

    def __init__(self,seed):
        """
            Inizializza lo schema di crittografia Fernet con una chiave.
            Se la chiave non è fornita, ne genera una nuova.
        """
        if seed is None:
            key = os.urandom(c.KEY_LENGTH)
        key = os.urandom(c.KEY_LENGTH,seed=seed)
        key = Key(key)
        self.IV = os.urandom(c._IV_SIZE,seed=seed)
        super().__init__(key)
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=c.KEY_LENGTH,
            salt=None,
            info=b'',
        )
        derived_keys = hkdf.derive(self._key.get_key())
        self._encryption_key = derived_keys[:self._AES_KEY_SIZE]
        self._auth_key = derived_keys[self._AES_KEY_SIZE:]
            
    def encrypt(self, message: Message) -> Message:
        """
            Metodo per crittografare un messaggio.
            Utilizza la chiave Fernet per crittografare il messaggio.
        """
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message.get_content().encode('utf-8')) + padder.finalize()
        cipher = Cipher(algorithms.AES(self._encryption_key), modes.CBC(self.IV))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        data_to_authenticate = self.IV + ciphertext
        mac = hmac.new(self._auth_key, data_to_authenticate, hashlib.sha256).digest()
        new_content = (self.IV + ciphertext + mac).hex()
        return Message(new_content,signature = None)


    def decrypt(self, message: Message) -> Message:
        """
            Metodo per decrittografare un messaggio.
            Utilizza la chiave Fernet per decrittografare il messaggio.
        """
        if not self.verify(message):
            raise ValueError("Il messaggio non è autentico o è stato manomesso.")
        data = bytes.fromhex(message.get_content())
        ciphertext = data[c._IV_SIZE:-c._MAC_SIZE]
        cipher = Cipher(algorithms.AES(self._encryption_key), modes.CBC(data[:c._IV_SIZE]))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_data) + unpadder.finalize()
        return Message(plaintext.decode('utf-8'))
       
    
    def sign(self, message: Message) -> Message:
        """
            Metodo per applicare le proprietà di autenticità e integrità al messaggio.
            In questo caso, la firma è semplicemente la crittografia del messaggio.
        """
        content_bytes = message.get_content().encode('utf-8')
        mac = hmac.new(self._auth_key, content_bytes, hashlib.sha256).digest()
        return Message(message.get_content(),signature=mac)
        
        
        
    def verify(self, message: Message) -> Message:
        """
            Metodo per verificare l'autenticità e integrità di un messaggio.
            In questo caso, la verifica è semplicemente la decrittografia del messaggio.
        """
        try: 
            payload = bytes.fromhex(message.get_content())
            if len (payload) < c._IV_SIZE + c._MAC_SIZE:
                return False
            mac_to_verify = payload[-c._MAC_SIZE:]
            cipher = payload[c._IV_SIZE:-c._MAC_SIZE]
            data_to_authenticate = payload[:c._IV_SIZE] + cipher
            h = hmac.new(self._auth_key, data_to_authenticate, hashlib.sha256)
            return hmac.compare_digest(h.digest(), mac_to_verify)
        except ValueError:
            return False

    