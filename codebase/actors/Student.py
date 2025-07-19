import json
from constants import Credential
from communication.Encryption_Scheme import Encryption_Scheme
from communication.User import User
class Student(User):
    """
        Classe che rappresenta uno studente nel sistema.
    """

    def __init__(self, name, surname, code):
        super().__init__(code)
        self._surname = surname
        self._name = name
        self._passwords = {}
        self._credential:Credential|None = None
        self._credential_ID: str | None = None

    def get_name(self):
        return self._name

    def get_surname(self):
        return self._surname
    
    def __str__(self):
        return f"Studente: {self._name} {self._surname}, Codice: {self._code}"
    
    def save_on_json(self) -> dict:
        dict = super().save_on_json()
        dict["user_type"] = "Student"
        dict["name"] = self._name
        dict["surname"] = self._surname
        dict["credential"] = json.dumps(self._credential)
        dict["credential_ID"] = self._credential_ID
        dict["passwords"] = self._passwords
        return dict
    
    @staticmethod
    def load_from_json(data: dict) -> 'Student':
        name = data["name"]
        surname = data["surname"]
        code = data["code"]
        student = Student(name, surname, code)
        student._credential = json.loads(data.get("credential", "{}"))
        student._credential_ID = data.get("credential_ID", None)
        student._keys = {key: Encryption_Scheme.load_from_json(value) for key, value in data.get("keys", {}).items()}
        student._passwords = data.get("passwords", {})
        return student
    
    def set_password(self, password: str, user:User):
        """
            Imposta la password dello studente per l'utente specificato.
        """
        self._passwords[user.get_code()] = password

    def get_password(self, user:User) -> str:
        """
            Restituisce la password dello studente per l'utente specificato.
        """
        return self._passwords.get(user.get_code(), "")
    
    def save_credential(self, credential:Credential, credential_ID: str) -> None:
        """
            Salva la credenziale dello studente.
        """
        self._credential = credential
        self._credential_ID = credential_ID

    def get_credential_data(self) -> tuple[Credential, str]:
        """
            Restituisce la credenziale dello studente e il suo ID.
        """
        if self._credential is None or self._credential_ID is None:
            raise ValueError("Credenziale non impostata.")
        return self._credential, self._credential_ID
    
    def get_label(self) -> str:
        return self._name + " " + self._surname