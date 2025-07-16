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

    def get_name(self):
        return self._name

    def get_surname(self):
        return self._surname
    
    def __str__(self):
        return f"Studente: {self._name} {self._surname}, Codice: {self._code}"
    
    def save_on_json(self) -> dict:
        dict = super().save_on_json()
        # dict["user_type"] = "Student"
        dict["name"] = self._name
        dict["surname"] = self._surname
        return dict
    
    @staticmethod
    def load_from_json(data: dict) -> 'Student':
        name = data["name"]
        surname = data["surname"]
        code = data["code"]
        student = Student(name, surname, code)
        #"keys": {user.get_name(): self._keys[user].save_on_json() for user in self._keys.keys()}
        student._keys = {key: Encryption_Scheme.load_from_json(value) for key, value in data.get("keys", {}).items()}
        return student
    
    def set_password(self, password: str, user:User):
        self._passwords[user.get_code()] = password

