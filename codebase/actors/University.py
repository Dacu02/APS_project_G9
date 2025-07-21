from datetime import date, timedelta
from typing import TypedDict, override
from actors.Student import Student
from communication.Hash_Algorithm import Hash_Algorithm
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from constants import CREDENTIAL_PERIOD_DAYS, DATA_DIRECTORY, UNIVERSITIES_FOLDER, Activity, ActivityResult, Credential, Exam, ExamResult, StudyPlan, EXCHANGE_DEFAULT_PERIOD_DAYS
from communication.Encryption_Scheme import Encryption_Scheme
from communication.User import User
import os
import json


class StudentData(TypedDict):
    name: str
    surname: str
    study_plan: str
    passed_exams: dict[str, ExamResult]
    passed_activities: dict[str, ActivityResult]
    password: str
    salt: str
    exchange_plan: dict[str, Exam | Activity] | None
    exchange_plan_data: dict | None
    credential: Credential | None
    credential_ID: str | None


class University(User):
    """
        Classe che rappresenta un'università nel sistema.
    """

    def __init__(self, name:str, code:str, password_hash_algorithm:Hash_Algorithm, study_plans:dict[str, StudyPlan] = {}, activities:dict[str, Activity] = {}, students:dict[str, StudentData]|None = None):
        """
            Inizializza un'istanza di University.
            Parametri:
            - name: Nome dell'università.
            - code: Codice identificativo dell'università.
            - study_plans: Dizionario dei piani di studio dell'università.
            - activities: Dizionario delle attività didattiche dell'università.
            - password_hash_algorithm: Algoritmo di hashing delle password
        """
        super().__init__(code)
        self._name = name
        self._study_plans = study_plans
        self._activities = activities
        if students:
            self._students: dict[str, StudentData] = students
        self._hash = password_hash_algorithm

        if students:
            for student in students:
                plan = students[student].get("study_plan")
                if plan not in self._study_plans:
                    raise ValueError(f"Il piano di studi {plan} non è presente nell'università {self._name}.")
                
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        if not os.path.exists(json_path):
            with open(json_path, "w") as f:
                json.dump(students if students else {}, f, indent=4)
        if not students:
            with open(json_path, "r") as f:
                data = json.load(f)
            self._students = {code: stud for code, stud in data.items()}

    def __str__(self) -> str:
        return f"Università: {self._name}, Codice: {self._code}"

    def get_name(self) -> str:
        return self._name
    
    def save_on_json(self) -> dict:
        dict = super().save_on_json()
        # dict["user_type"] = "University"
        dict["study_plans"] = self._study_plans
        dict["activities"] = self._activities
        dict["name"] = self._name
        dict["hash"] = self._hash.save_on_json()
        return dict

    def get_study_plans(self) -> dict[str, StudyPlan]:
        return self._study_plans

    @staticmethod
    def load_from_json(data: dict) -> 'University':
        name = data["name"]
        code = data["code"]
        hashing_algorithm = Hash_Algorithm.load_from_json(data["hash"])
        study_plans: dict[str, StudyPlan] = data.get("study_plans", {})
        activities: dict[str, Activity] = data.get("activities", {})
        university = University(name, code, hashing_algorithm, study_plans, activities)
        university._keys = {key: Encryption_Scheme.load_from_json(value) for key, value in data.get("keys", {}).items()}
        return university
    
    def set_public_key(self, public_key: Asymmetric_Scheme):
        """
            Imposta la chiave pubblica dell'università.
            La imposta a sè stessa, siccome è la propria.
        """
        self.add_key(self, public_key)

    def is_incoming_student(self, student:Student):
        """
            Verifica se uno studente è in arrivo presso l'università.
            Parametri:
            - student: Lo studente da verificare.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        return serial_id in self._students and self._students[serial_id].get("exchange_plan_data")

    def enroll_student(self, student: Student, password:str, study_plan: str):
        """
            Iscrive uno studente all'università con un piano di studi specificato.
            Parametri:
            - student: Lo studente da iscrivere.
            - password: La password da associare allo studente.
            - study_plan: Il nome piano di studi a cui lo studente si immatricola
        """
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)

        student_id = student.get_code()
        serial_id = f"{int(student_id):03d}#{int(self._code):03d}"

        scheme = self._keys.get(self._code)
        if scheme is None or not isinstance(scheme, Asymmetric_Scheme):
            raise ValueError("L'università non possiede uno schema crittografico asimmetrico.")

        if serial_id in self._students.keys():
            if self._students[serial_id].get("exchange_plan_data") and not self._students[serial_id]["password"]: # Se lo studente è già iscritto ma senza password, aggiorna la password
                
                self._students[serial_id]["password"] = self._hash.hash(password + self._students[serial_id]["salt"])

                data[serial_id] = self._students[serial_id]
                with open(json_path, "w") as f:
                    json.dump(data, f, indent=4)

                return
            raise ValueError(f"Lo studente {student_id} è già iscritto all'università {self._name}.")

        salt = student.get_name() + student.get_surname()  # Per semplicità si considera la concatenazione del nome e cognome come salt
        student_data: StudentData = {
            "name": student.get_name(),
            "surname": student.get_surname(),
            "study_plan": str(study_plan),
            "passed_exams": {},
            "passed_activities": {},
            "salt": salt,
            "password": self._hash.hash(password + salt),
            "exchange_plan": None,
            "exchange_plan_data": None,
            "credential": None,
            "credential_ID": None,
        }

        self._students[serial_id] = student_data
        data[serial_id] = student_data
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def check_password(self, student: Student, password: str) -> bool:
        """
            Verifica la password dello studente.
            Parametri:
            - student: Lo studente di cui verificare la password.
            - password: La password da verificare.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        if serial_id not in self._students.keys():
            raise ValueError(f"Lo studente {student.get_code()} non è iscritto all'università {self._name}.")
        
        student_data = self._students[serial_id]
        stored_password = student_data.get("password")
        # salt = student_data.get("salt", "") # TODO Implementa il salt
        
        scheme = self._keys.get(self._code)
        if scheme is None or not isinstance(scheme, Asymmetric_Scheme):
            raise ValueError("L'università non possiede uno schema crittografico asimmetrico.")

        return self._hash.hash(password + student_data.get("salt", "")) == stored_password

    def add_study_plan(self, plan_name: str, study_plan: StudyPlan):
        """
            Aggiunge un piano di studi all'università.
        """
        if plan_name not in self._study_plans:
            json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json")
            with open(json_path, "r") as f:
                data = json.load(f)
            data[self._code]["study_plans"][plan_name] = study_plan
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)
            self._study_plans[plan_name] = study_plan
            print(f"Piano di studi {plan_name} aggiunto all'università {self._name}.")
        else:
            raise ValueError(f"Il piano di studi {study_plan} è già presente nell'università {self._name}.")

    def add_activity(self, activity: Activity):
        """
            Aggiunge un'attività didattica all'università.
        """
        activity_name = activity['name']
        cfus = activity['cfus']
        if cfus < 0:
            raise ValueError("I CFU dell'attività devono essere un numero positivo.")
        if activity_name not in self._activities:
            json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json")
            with open(json_path, "r") as f:
                data = json.load(f)
            data[self._code]["activities"][activity_name] = {"name": activity_name, "cfus": cfus}
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)
            self._activities[activity_name] = {"name": activity_name, "cfus": cfus}
            print(f"Attività {activity_name} aggiunta all'università {self._name}.")
        else:
            raise ValueError(f"L'attività {activity_name} è già presente nell'università {self._name}.")

    def agree_exchange_contract(self, student:Student, destination_university: 'University', study_plan: StudyPlan, activities: list[Activity], internal_referrer: str):
        """
            Registra un contratto di scambio per uno studente.
            Parametri:
            - student: Lo studente che partecipa allo scambio.
            - destination_university: L'università di destinazione dello scambio.
            - study_plan: Il piano di studi dell'università di destinazione.
            - activities: Le attività previste per lo scambio.
            - internal_referrer: Il referente interno dell'università.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        if serial_id not in data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")

        self._students[serial_id]["exchange_plan_data"] = {
            "destination_university": {'code': destination_university.get_code(), 'name': destination_university.get_name()},
            "exams": {exam["name"]: exam["cfus"] for exam in study_plan},
            "activities": {activity["name"]: activity["cfus"] for activity in activities},
            "internal_referrer": internal_referrer
        }

        data[serial_id] = self._students[serial_id]
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def accept_incoming_exchange(self, student: Student, incoming_university: 'University', incoming_serial_id: str, incoming_referrer: str, internal_referrer: str, exchange_period_days: int = EXCHANGE_DEFAULT_PERIOD_DAYS):
        """
            Accetta un contratto di scambio in arrivo per uno studente.
            Parametri:
            - student: Lo studente che partecipa al periodo all'estero.
            - incoming_university: L'università di provenienza dello studente.
            - incoming_serial_id: La matricola dello studente nell'università di provenienza.
            - incoming_referrer: Il referente dell'università di provenienza.
            - internal_referrer: Il referente interno dell'università.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")

        with open(json_path, "r") as f:
            data = json.load(f)

        student_data:StudentData = {
            "name": student.get_name(),
            "surname": student.get_surname(),
            "study_plan": "exchange",
            "passed_exams": {},
            "passed_activities": {},
            "password": "",
            "salt": student.get_name() + student.get_surname(),  # Per semplicità si considera la concatenazione del nome e cognome come salt
            "exchange_plan": None,
            "exchange_plan_data": {
                "incoming_university": {
                    "code": incoming_university.get_code(),
                    "name": incoming_university.get_name()
                },
                "incoming_serial_id": incoming_serial_id,
                "incoming_referrer": incoming_referrer,
                "internal_referrer": internal_referrer,
                "exchange_period_start": date.today().isoformat(),
                "exchange_period_end": (date.today() + timedelta(days=exchange_period_days)).isoformat()
            },
            "credential": None,
            "credential_ID": None
        }

        self._students[serial_id] = student_data

        data[serial_id] = self._students[serial_id]
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
            

    def pass_exam(self, student: Student, results: ExamResult):
        """
            Registra il superamento di un esame da parte dello studente.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        
        if serial_id not in self._students.keys():
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        if "passed_exams" not in self._students[serial_id]:
            self._students[serial_id]["passed_exams"] = {}

        self._students[serial_id]["passed_exams"][results["name"]] = results

        data[serial_id] = self._students[serial_id]
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def pass_activity(self, student: Student, results: ActivityResult):
        """
            Registra il superamento di un'attività da parte dello studente.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        
        if serial_id not in self._students.keys():
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        if "passed_activities" not in self._students[serial_id]:
            self._students[serial_id]["passed_activities"] = {}

        self._students[serial_id]["passed_activities"][results["name"]] = results

        data[serial_id] = self._students[serial_id]
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_student_credential(self, student:Student) -> Credential:
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"

        if serial_id not in self._students.keys():
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")

        exchange_plan_data = self._students[serial_id].get("exchange_plan_data")
        if not exchange_plan_data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è in mobilità.")
        
        incoming_uni_serial_id = exchange_plan_data.get("incoming_serial_id")
        if not incoming_uni_serial_id:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non ha un ID di mobilità in entrata.")

        credential = self._students[serial_id]['credential']
        if credential:
            expiration_date = credential.get("expiration_date")
            if expiration_date and date.fromisoformat(expiration_date) >= date.today():
                return credential
            
        return self._create_student_credential(student)

    def _create_student_credential(self, student:Student) -> Credential:
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        student_data = self._students[serial_id]
        
        if not student_data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non ha dati registrati.")
        
        exchange_plan_data = student_data['exchange_plan_data']

        if not exchange_plan_data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non ha un piano di scambio registrato.")

        incoming_uni_serial_id = exchange_plan_data.get("incoming_serial_id")

        passed_exams:list[ExamResult] = [] 
        for key, exam_value in student_data.get("passed_exams", {}).items():
            passed_exams.append(exam_value)

        passed_activities:list[ActivityResult] = []
        for key, activity_value in student_data.get("passed_activities", {}).items():
            passed_activities.append(activity_value)

        credential: Credential = {
            "internal_serial_id": incoming_uni_serial_id, # type: ignore
            "external_serial_id": serial_id,
            "name": student_data.get("name"),
            "surname": student_data.get("surname"),
            "internal_referrer": student_data.get("incoming_referrer", None),
            "external_referrer": student_data.get("internal_referrer", None),
            "external_university": self._name,
            "external_university_code": self._code,
            "emission_date": date.today().isoformat(),
            "expiration_date": (date.today() + timedelta(days=CREDENTIAL_PERIOD_DAYS)).isoformat(),
            "exchange_period_start": student_data.get("exchange_period_start", None),
            "exchange_period_end": student_data.get("exchange_period_end", None),
            "exams_results": passed_exams,
            "activities_results": passed_activities,
        }

        self._students[serial_id]["credential"] = credential

        # Salva i nuovi dati della credenziale su file JSON
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
            data[serial_id]["credential"] = credential
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        return credential

    def set_credential_id(self, student:Student, ID:str) -> None:
        """
            Imposta l'ID della credenziale per uno studente.
            Parametri:
            - student: Lo studente di cui impostare l'ID della credenziale.
            - ID: L'ID da impostare.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        if serial_id not in self._students.keys():
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        self._students[serial_id]["credential_ID"] = ID
        # Salva i nuovi dati della credenziale su file JSON
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)

        data[serial_id]["credential_ID"] = ID
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_credential_id(self, student:Student) -> str|None:
        """
            Ottiene l'ID della credenziale per uno studente.
            Parametri:
            - student: Lo studente di cui ottenere l'ID della credenziale.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        if serial_id not in self._students.keys():
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        return self._students[serial_id]["credential_ID"]

    def check_matching(self, student: Student, credential: Credential) -> bool:
        """
            Verifica se la credenziale dello studente corrisponde a quella dell'università.
            Parametri:
            - student: Lo studente di cui verificare la credenziale.
            - credential: La credenziale da verificare.
        """
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        if serial_id not in self._students.keys():
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        credential_exams_list = credential.get("exams_results", [])
        credential_activities_list = credential.get("activities_results", [])
        credential_destination_university = credential.get("external_university", None)

        student_data = self._students[serial_id]
        if not student_data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non ha dati registrati.")
        exchange_plan_data = student_data["exchange_plan_data"]

        if not exchange_plan_data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non ha un piano di scambio registrato.")
        
        if exchange_plan_data.get("destination_university", {}).get("name") != credential_destination_university:
            raise ValueError(f" [{self._name}] La destinazione dello scambio non corrisponde alla credenziale dello studente {student.get_code()}.")

        credential_internal_serial_id = credential.get("internal_serial_id")
        if credential_internal_serial_id != serial_id:
            raise ValueError(f" [{self._name}] La matricola dello studente {student.get_code()} non corrisponde a quella presente nella credenziale.")

        credential_expiration_date = credential.get("expiration_date")
        if credential_expiration_date and date.fromisoformat(credential_expiration_date) < date.today():
            raise ValueError(f" [{self._name}] La credenziale dello studente {student.get_code()} è scaduta.")

        exchange_exams = exchange_plan_data.get("exams", {})
        exchange_activities = exchange_plan_data.get("activities", {})

        for exam, cfu in exchange_exams.items():
            found = False
            for exam_result in credential_exams_list:
                if not found and exam_result["name"] == exam:
                    if cfu > exam_result["cfus"]:
                        raise ValueError(f" [{self._name}] I CFU dell'esame {exam} nella credenziale dello studente {student.get_label()} sono inferiori a quelli previsti nel piano di scambio.")
                    found = True
            if not found:
                raise ValueError(f" [{self._name}] L'esame {exam} non è presente nella credenziale dello studente {student.get_label()}.")

        for activity, cfu in exchange_activities.items():
            found = False
            for activity_result in credential_activities_list:
                if not found and activity_result["name"] == activity:
                    if cfu > activity_result["cfus"]:
                        raise ValueError(f" [{self._name}] I CFU dell'attività {activity} nella credenziale dello studente {student.get_label()} sono inferiori a quelli previsti nel piano di scambio.")
                    found = True
            if not found:
                raise ValueError(f" [{self._name}] L'attività {activity} non è presente nella credenziale dello studente {student.get_label()}.")
            
        return True
        # Se tutte le verifiche sono superate, la credenziale è valida

    def check_exam_availability(self, exam:Exam) -> bool:
        """
            Verifica la disponibilità di un esame nel piano di studi.
            Parametri:
            - exam: L'esame da verificare.
        """
        name = exam["name"]
        cfus = exam["cfus"]
        for study_plan in self._study_plans.values():
            for exam_plan in study_plan:
                if exam_plan["name"] == name and exam_plan["cfus"] >= cfus:
                    return True
        return False

    def check_activity_availability(self, activity:Activity) -> bool:
        """
            Verifica la disponibilità di un'attività didattica nel piano di studi.
            Parametri:
            - activity: L'attività da verificare.
        """
        name = activity["name"]
        cfus = activity["cfus"]
        if name in self._activities and self._activities[name]["cfus"] >= cfus:
            return True
        return False
    
    def get_label(self) -> str:
        return self._name
    
    def set_credential(self, student:Student, credential:Credential|None, credentia_id:str|None):
        serial_id = f"{int(student.get_code()):03d}#{int(self._code):03d}"
        if serial_id not in self._students.keys():
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")

        self._students[serial_id]["credential"] = credential
        self._students[serial_id]["credential_ID"] = credentia_id

        # Salva i nuovi dati della credenziale su file JSON
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        data[serial_id]["credential"] = credential
        data[serial_id]["credential_ID"] = credentia_id
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)