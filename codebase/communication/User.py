from abc import ABC, abstractmethod


from communication.Symmetric_Scheme import Symmetric_Scheme
from constants import PRINT_MAX_LENGTH, DECORATION_CHARACTERS
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

    def send(self, user: "User", message: Message, encrypt: bool = True, sign: bool = True):
        """
            Invia un messaggio ad un altro utente, controlla gli schemi di crittografia a disposizione.
            Se l'utente ha uno schema di crittografia simmetrico condiviso con l'utente destinatario, lo utilizza per cifrare e applicare un token sul messaggio.
            Se l'utente ha la chiave pubblica dello schema di crittografia asimmetrico dell'utente destinatario, la utilizza per cifrare il messaggio
            Se l'utente ha una chiave privata, la utilizza per firmare il messaggio.
            Parametri:
            - user: L'utente destinatario del messaggio.
            - message: Il messaggio da inviare.
            - encrypt: Il messaggio dev'essere cifrato
            - sign: Il messaggio dev'essere firmato
        """
        destination_scheme = self._keys.get(user.get_code())
        print("\n" + ">"*DECORATION_CHARACTERS + f" {self.get_label()} INVIA UN MESSAGGIO A {user.get_label()} " + ">"*DECORATION_CHARACTERS)
        if encrypt:
            if not destination_scheme:
                raise ValueError(f"{self.get_label()} non ha uno schema di crittografia per l'utente {user.get_label()}")
            elif isinstance(destination_scheme, Asymmetric_Scheme):
                mex = destination_scheme.encrypt(message)
                if sign:
                    scheme = self._keys.get(self.get_code())
                    if not scheme:
                        raise ValueError(f"{self.get_label()} non ha uno schema di crittografia per se firmare")
                    mex = scheme.sign(mex)
                print(f"[{self.get_label()}->{user.get_label()}] cifra con la chiave pubblica di destinazione {"e firma con la privata" if sign else ""}")
            else:
                mex = destination_scheme.encrypt(message)
                if sign:
                    mex = destination_scheme.sign(mex)
                print(f"[{self.get_label()}->{user.get_label()}] cifra {"e firma" if sign else ""} il messaggio con lo schema di crittografia simmetrico condiviso")
        else:
            mex = message
            if sign:
                scheme = self._keys.get(self.get_code())
                if not scheme:
                    raise ValueError(f"{self.get_label()} non ha uno schema di crittografia per se firmare")
                mex = scheme.sign(mex)
            print(f"[{self.get_label()}->{user.get_label()}] invia il messaggio in chiaro{" e firma con la propria chiave privata" if sign else ""}")
        print("Il messaggio inviato è: ", message.get_content())
        user._receive(self, mex, decrypt=encrypt, verify=sign)

    def _receive(self, user: "User", message: Message, decrypt: bool = True, verify: bool = True):
        """
            Riceve un messaggio da un altro utente, controlla gli schemi di crittografia a disposizione.
            Se l'utente ha uno schema di crittografia simmetrico condiviso con l'utente mittente, lo utilizza per decifrare e verificare il token sul messaggio.
            Se l'utente ha una propria chiave privata, la utilizza per decifrare il messaggio.
            Se l'utente ha la chiave pubblica dello schema di crittografia asimmetrico dell'utente mittente, la utilizza per verificare il messaggio.
            - Parametri:
            - user: L'utente mittente del messaggio.
            - message: Il messaggio da ricevere.
            - decrypt: Il messaggio dev'essere decifrato
            - verify: Il messaggio dev'essere verificato
        """
        source_scheme = self._keys.get(user.get_code())
        scheme = self._keys.get(self.get_code())
        if decrypt:
            if source_scheme and isinstance(source_scheme, Symmetric_Scheme):
                mex = source_scheme.decrypt(message)
                print(f"[{self.get_label()}<-{user.get_label()}] decritta il messaggio con lo schema di crittografia simmetrico condiviso")
                if verify:
                    result = source_scheme.verify(message)
                    if not result:
                        print("Il messaggio è stato manomesso.")
                        return
                    print(f"[{self.get_label()}<-{user.get_label()}] verifica il MAC del messaggio")
                self._last_message = mex
            else:
                if not scheme:
                    raise ValueError(f"{self.get_label()} non ha uno schema di crittografia per decifrare il messaggio")
                else:
                    mex = scheme.decrypt(message)
                    print(f"[{self.get_label()}<-{user.get_label()}] decritta il messaggio con la propria chiave privata")
                if verify:
                    if source_scheme and isinstance(source_scheme, Asymmetric_Scheme):
                        result = source_scheme.verify(message)
                        if not result:
                            print("Il messaggio è stato manomesso.")
                            return
                        print(f"[{self.get_label()}<-{user.get_label()}] verifica la firma del messaggio con la chiave pubblica del mittente")
                    else:
                        raise ValueError(f"{self.get_label()} non ha uno schema di crittografia per verificare il messaggio")
                self._last_message = mex
        else:
            mex = message
            print(f"[{self.get_label()}<-{user.get_label()}] riceve il messaggio in chiaro")
        if verify and not decrypt:
            if source_scheme and isinstance(source_scheme, Asymmetric_Scheme):
                result = source_scheme.verify(message)
                if not result:
                    print("Il messaggio è stato manomesso.")
                    return
                print(f"[{self.get_label()}<-{user.get_label()}] verifica la firma del messaggio con la chiave pubblica del mittente")
            else:
                raise ValueError(f"{self.get_label()} non ha uno schema di crittografia per verificare il messaggio")
        self._last_message = mex
        print("<"*DECORATION_CHARACTERS + f" {self.get_label()} RICEVE UN MESSAGGIO DA {user.get_label()} " + "<"*DECORATION_CHARACTERS)

    def get_code(self) -> str:
        """
            Restituisce il codice dell'utente.
        """
        return self._code
    
    def get_label(self) -> str:
        """
            Restituisce l'etichetta dell'utente
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