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
                json.dump({}, f)
                
    def __str__(self):
        return f"CA: {self._code}"
    
    def register_user_public_key(self, user: User, public_key_scheme: Asymmetric_Scheme) -> Certificate:
        """
            Registra la chiave pubblica dell'utente.
        """
        self.add_key(user, public_key_scheme)
        file = os.path.join(DATA_DIRECTORY, CAs_FOLDER, f"ca_{self._code}.json")
        with open(file, "r") as f:
            data = json.load(f)

        scheme = self._keys[self._code] if self._code in self._keys else None
        if scheme is None:
            raise ValueError(f"[{self._code}] Chiave di crittografia non trovata per la CA {self._code}")
        if not isinstance(scheme, Asymmetric_Scheme):
            raise TypeError(f"[{self._code}] La chiave di crittografia non è di tipo Asymmetric_Scheme")

        certificate:CertificateContent = {
            "key": public_key_scheme.save_on_json(),
            "timestamp": datetime.datetime.now().isoformat(),
        }
        cert = Certificate(certificate, scheme)
        data[user.get_code()] = cert.save_on_json()
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

        return cert

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

    def get_user_certificate(self, user: User) -> Certificate | None:
        """
            Restituisce il certificato dell'utente registrato.
        """
        file = os.path.join(DATA_DIRECTORY, CAs_FOLDER, f"ca_{self._code}.json")
        with open(file, "r") as f:
            data = json.load(f)
        if user.get_code() in data:
            certificate_data = data[user.get_code()]
            return Certificate.load_from_json(certificate_data)
        return None

    def save_on_json(self) -> dict:
        """
            Metodo per salvare la CA su un dizionario, da cui poi si potrà generare un file JSON.
        """
        dict = super().save_on_json()
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
    