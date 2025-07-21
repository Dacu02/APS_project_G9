
from communication import Asymmetric_Scheme, Symmetric_Scheme
from communication import User, Message


class Attacker(User):
    def __init__(self, name: str):
        super().__init__(name)

    @staticmethod
    def load_from_json(data: dict):
        return User.load_from_json(data)
    
    def intercept_message(self, sender: User, receiver: User, message: Message, encrypt: bool = True, sign: bool = False) -> Message:
            """
            Funzione per intercettare i messaggi tra lo studente e l'università.
            """
            sign_scheme = encrypt_scheme = None

            out_scheme = sender._keys.get(receiver.get_code())
            in_scheme = sender._keys.get(sender.get_code())
            if out_scheme and isinstance(out_scheme, Symmetric_Scheme):
                sign_scheme = encrypt_scheme = out_scheme
            elif out_scheme and isinstance(out_scheme, Asymmetric_Scheme):
                sign_scheme = encrypt_scheme = in_scheme
            if (not sign_scheme and sign) or (not encrypt_scheme and encrypt):
                raise ValueError("Nessun schema di cifratura trovato")
            
            if encrypt: # Se il messaggio viene inviato già cifrato, l'attaccante non è in grado di decifrarlo
                mex = encrypt_scheme.encrypt(message) # Caso dello studente che invia un messaggio cifrato all'università
            else: # Se il messaggio non viene cifrato, l'attaccante può leggerlo
                mex = message
            if sign: # Se il messaggio viene firmato, l'attaccante non è in grado di forgiare una firma valida quando modifica il contenuto
                mex = sign_scheme.sign(mex) # Caso dell'università che invia un messaggio firmato allo studente
            return mex

    def inject_message(self, sender: User, receiver: User, message: Message, encrypt: bool = True, sign: bool = True) -> None:
        """
        Funzione per iniettare un messaggio tra lo studente e l'università.
        L'attaccante può modificare il contenuto del messaggio prima di inviarlo.
        """
        sender.send(receiver, message, encrypt=encrypt, sign=sign)