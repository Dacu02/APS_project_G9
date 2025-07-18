from abc import ABC, abstractmethod
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from communication.Message import Message
from communication.Encryption_Scheme import Encryption_Scheme
class User(ABC):
    """
        Classe astratta che rappresenta un utente del sistema.
        Gli utenti possono ricevere ed inviare messaggi ad altri utenti.
    """
    def __init__(self, code: str):
        super().__init__()
        self._code = code
        
        # Dizionario che associa gli utenti agli schemi di crittografia
        self._keys: dict[str, Encryption_Scheme] = {}
        self._last_message:Message

    def send(self, user: "User", message: Message, encrypt: bool = True, sign: bool = True, authority: bool = False):
        """
            Invia un messaggio ad un altro utente.
            Parametri:
            - user: L'utente destinatario del messaggio.
            - message: Il messaggio da inviare.
            - encrypt: Se True, il messaggio viene cifrato.
            - sign: Se True, il messaggio viene firmato.
            - authority: Se True, il messaggio viene inviato preservando la proprietà di autenticità attraverso la cifratura mediante chiave privata. Authority prevale su encrypt e sign.
        """

        if authority:
            scheme = self._keys.get(self._code)
            if scheme is None or not isinstance(scheme, Asymmetric_Scheme):
                raise ValueError(f"[{self._code}] Chiave di crittografia non trovata per l'utente {self._code}")

            mex = scheme.authority_sign(message)
            print(f"{self._code} cifra e firma il messaggio: {message.get_content()} con la propria chiave privata")
            user._receive(self, mex, decrypt=False, verify=True)

        if not encrypt and not sign:
            user._receive(self, message, decrypt=False, verify=False)
            return
        
        print(f"{self._code} invia a {user._code}: {message.get_content()}")
        if user.get_code() not in self._keys: # Se l'utente non ha una chiave per l'utente destinatario, controlla se ha una propria chiave
            if self._keys.get(self.get_code()) is not None:
                print(f"Nessuna chiave trovata per l'utente destinatario, {self._code} utilizza la propria chiave")
                scheme = self._keys[self.get_code()]
            else:
                raise ValueError(f"[{self._code}] Chiave di cifratura non trovata per l'utente {user._code}")
        else:
            scheme = self._keys[user.get_code()]

        mex = scheme.encrypt(message) if encrypt else message
        mex = scheme.sign(mex) if sign else mex
        print(f"{self._code} firma il messaggio: {mex.get_content()} con firma {mex.get_signature()}")
        print("Ha una firma?:", mex.get_signature() is not None)

        user._receive(self, mex, decrypt=encrypt, verify=sign)

    def _receive(self, user: "User", message: Message, decrypt: bool = True, verify: bool = True):
        """
            Riceve un messaggio da un altro utente.
            Parametri:
            - user: L'utente mittente del messaggio.
            - message: Il messaggio ricevuto.
            - decrypt: Se True, il messaggio viene decifrato.
            - verify: Se True, viene verificata la proprietà di integrità.
        """

        if not decrypt and not verify:
            print(f"{self._code} riceve il messaggio {message.get_content()} senza decifrare o verificare la firma.")
            return

        print(f"{self._code} riceve: {message.get_content()}")
            
        if user.get_code() not in self._keys: # Se l'utente non ha una chiave per l'utente mittente, controlla se ha una propria chiave
            if self._keys.get(self.get_code()) is not None:
                print(f"Nessuna chiave trovata per l'utente mittente, {self._code} utilizza la propria chiave")
                scheme = self._keys[self.get_code()]
            else:
                raise ValueError(f"[{self._code}] Chiave di decifratura non trovata per l'utente {user.get_code()}")
        else:
            scheme = self._keys[user.get_code()]

        mex = scheme.decrypt(message) if decrypt else message

        if message.get_signature() is not None and verify:
            print(f"{self._code} verifica la firma: {message.get_signature()}")
            if scheme.verify(message):
                print(f"{self._code} firma verificata con successo")
            else:
                print(f"{self._code} firma non valida, messaggio rigettato")
        else:
            print(f"{self._code} non ha una firma da verificare o la verifica non è richiesta")
        
        print(f"{self._code} ha aperto il messaggio: {mex.get_content()}")
        
        self._last_message = mex


    def get_code(self) -> str:
        """
            Restituisce il codice dell'utente.
        """
        return self._code

    def save_on_json(self) -> dict:
        """
            Metodo per salvare l'utente su un dizionario, da cui poi si potrà generare un file JSON.
        """
        return {
            "code": self._code,
            "keys": {user: scheme.save_on_json() for user, scheme in self._keys.items()}
        }

    @staticmethod
    @abstractmethod
    def load_from_json(data: dict) -> "User":
        """
            Metodo astratto per caricare l'utente da un dizionario, ottenuto da un file JSON.
            Deve essere implementato dalle classi derivate.
        """
        from actors.Student import Student
        from actors.University import University
        from actors.CA import CA
        user_type = data["user_type"]
        if user_type == "Student":
            return Student.load_from_json(data)
        elif user_type == "University":
            return University.load_from_json(data)
        elif user_type == "CA":
            return CA.load_from_json(data)
        else:
            raise ValueError(f"Tipo di utente sconosciuto: {user_type}")

    def add_key(self, user: "User", scheme: Encryption_Scheme|None):
        """
            Aggiunge una chiave di crittografia per un utente specifico.
        """
        if not scheme:
            del self._keys[user.get_code()]
        else:
            self._keys[user.get_code()] = scheme


    def get_last_message(self) -> Message:
        """
            Restituisce l'ultimo messaggio ricevuto dall'utente.
        """
        return self._last_message