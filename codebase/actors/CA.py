import json
import os
from communication.Certificate import Certificate, CertificateContent
from communication.Key import Key
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from constants import DATA_DIRECTORY, CAs_FOLDER
from communication.Encryption_Scheme import Encryption_Scheme
from communication.User import User
from communication.Message import Message
import datetime


class CA(User):
    """
        Classe che rappresenta una Certification Authority (CA).
    """
    def __init__(self, code):
        super().__init__(code)
        json_path = os.path.join(DATA_DIRECTORY, CAs_FOLDER, f"ca_{self._code}.json")
        if not os.path.exists(json_path):
            with open(json_path, "w") as f:
                f.write("{}")
                
    def __str__(self):
        return f"CA: {self._code}"
    
    def register_user_public_key(self, user: User, public_key_scheme: Asymmetric_Scheme):
        """
            Registra la chiave pubblica dell'utente.
        """
        public_key_scheme = public_key_scheme
        self.add_key(user, public_key_scheme)
        file = os.path.join(DATA_DIRECTORY, CAs_FOLDER, f"ca_{self._code}.json")
        with open(file, "r") as f:
            data = json.load(f)

        scheme = self._keys[self._code] if self._code in self._keys else None
        if scheme is None:
            raise ValueError(f"[{self._code}] Chiave di crittografia non trovata per la CA {self._code}")
        if not isinstance(scheme, Asymmetric_Scheme):
            raise TypeError(f"[{self._code}] La chiave di crittografia non è di tipo Asymmetric_Scheme")
        
        key_string = public_key_scheme.get_public_key()
        if not isinstance(key_string, Key):
            raise TypeError(f"[{self._code}] La chiave pubblica deve essere di tipo Key, ma è di tipo {type(key_string)}")
        
        key_string = key_string.save_on_json().get("key")
        if not isinstance(key_string, str):
            raise TypeError(f"[{self._code}] La chiave pubblica deve essere una stringa, ma è di tipo {type(key_string)}")

        certificate:CertificateContent = {
            "key": key_string,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        cert = Certificate(certificate, scheme)
        data[user.get_code()] = cert.save_on_json()
        json.dump(data, f, indent=4)

    def get_user_public_key(self, user: User) -> tuple[Asymmetric_Scheme, str] | None:
        """
            Restituisce la chiave pubblica dell'utente registrato, salvata nel certificato.
        """
        file = os.path.join(DATA_DIRECTORY, CAs_FOLDER, f"ca_{self._code}.json")
        with open(file, "r") as f:
            data = json.load(f)
        if user.get_code() in data:
            certificate = data[user.get_code()]
            public_key_data = certificate.get("key", None)
            if public_key_data:
                return Asymmetric_Scheme.load_from_json(public_key_data), certificate["signature"]
        return None

    def save_on_json(self) -> dict:
        """
            Metodo per salvare la CA su un dizionario, da cui poi si potrà generare un file JSON.
        """
        dict = super().save_on_json()
        # dict["user_type"] = "CA"
        return dict
    
    @staticmethod
    def load_from_json(data: dict) -> 'CA':
        """
            Metodo per caricare la CA da un dizionario.
        """
        code = data["code"]
        ca = CA(code)
        ca._keys = {key: Encryption_Scheme.load_from_json(value) for key, value in data.get("keys", {}).items()}
        return ca
    