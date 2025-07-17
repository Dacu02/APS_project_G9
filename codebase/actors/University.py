from datetime import date
from typing import TypedDict
from actors.Student import Student
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from constants import DATA_DIRECTORY, UNIVERSITIES_FOLDER, Activity, ActivityResult, Exam, ExamResult, StudyPlan
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


class University(User):
    """
        Classe che rappresenta un'università nel sistema.
    """

    def __init__(self, name:str, code:str, study_plans:dict[str, StudyPlan] = {}, activities:dict[str, Activity] = {}, students:dict[str, StudentData] = {}):
        """
            Inizializza un'istanza di University.
            Parametri:
            - name: Nome dell'università.
            - code: Codice identificativo dell'università.
            - study_plans: Dizionario dei piani di studio dell'università.
            - activities: Dizionario delle attività didattiche dell'università.
        """
        super().__init__(code)
        self._name = name
        self._study_plans = study_plans
        self._activities = activities
        self._students = students

        for student in students:
            plan = students[student].get("study_plan")
            if plan not in self._study_plans:
                raise ValueError(f"Il piano di studi {plan} non è presente nell'università {self._name}.")

        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        if not os.path.exists(json_path):
            with open(json_path, "w") as f:
                f.write("{}")

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
        dict['students'] = json.dumps(self._students)
        return dict

    def get_study_plans(self) -> dict[str, StudyPlan]:
        return self._study_plans

    @staticmethod
    def load_from_json(data: dict) -> 'University':
        name = data["name"]
        code = data["code"]
        study_plans: dict[str, StudyPlan] = data.get("study_plans", {})
        activities: dict[str, Activity] = data.get("activities", {})
        students: dict[str, StudentData] = data.get("students", {})
        university = University(name, code, study_plans, activities, students)
        university._keys = {key: Encryption_Scheme.load_from_json(value) for key, value in data.get("keys", {}).items()}
        return university
    
    def set_public_key(self, public_key: Asymmetric_Scheme):
        """
            Imposta la chiave pubblica dell'università.
            La imposta a sè stessa, siccome è la propria.
        """
        self.add_key(self, public_key)

    def enroll_student(self, student: 'Student', password, study_plan: str):
        """
            Iscrive uno studente all'università con un piano di studi specificato.
            Parametri:
            - student: Lo studente da iscrivere.
            - study_plan: Il nome piano di studi a cui lo studente si immatricola
        """
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)

        student_id = student.get_code()
        serial_id = f"{student_id:03d}#{self._code:03d}" #TODO Controllare eventualmente in fase di input se sono corretti in lunghezza?

        if 'students' not in data.keys():
            data['students'] = {}
        if serial_id in data['students'].keys():
            raise ValueError(f"Lo studente {student_id} è già iscritto all'università {self._name}.")

        scheme = self._keys.get(self._code)
        if scheme is None or not isinstance(scheme, Asymmetric_Scheme):
            raise ValueError("L'università non possiede uno schema crittografico asimmetrico.")

        student_data: StudentData = {
            "name": student.get_name(),
            "surname": student.get_surname(),
            "study_plan": str(study_plan),
            "passed_exams": {},
            "passed_activities": {},
            "password": scheme.hash(password),
            "salt": student.get_name() + student.get_surname(), # Per semplicità si considera la concatenazione del nome e cognome come salt
            "exchange_plan": None
        }

        data['students'][serial_id] = student_data

        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

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
        serial_id = f"{student.get_code():03d}#{self._code:03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        if serial_id not in data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        data[serial_id]["exchange_plan"] = {}
        data[serial_id]["exchange_plan"]['destination_university'] = {'code':destination_university.get_code(), 'name':destination_university.get_name()}
        data[serial_id]["exchange_plan"]['exams'] = {exam["name"]: exam["cfus"] for exam in study_plan}
        data[serial_id]["exchange_plan"]['activities'] = {activity["name"]: activity["cfus"] for activity in activities}
        data[serial_id]["exchange_plan"]['internal_referrer'] = internal_referrer
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def accept_incoming_exchange(self, student: Student, incoming_university: 'University', incoming_serial_id: str, incoming_referrer: str, internal_referrer: str):
        """
            Accetta un contratto di scambio in arrivo per uno studente.
            Parametri:
            - student: Lo studente che partecipa al periodo all'estero.
            - incoming_university: L'università di provenienza dello studente.
            - incoming_serial_id: La matricola dello studente nell'università di provenienza.
            - incoming_referrer: Il referente dell'università di provenienza.
            - internal_referrer: Il referente interno dell'università.
        """
        serial_id = f"{student.get_code():03d}#{self._code:03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)

        data[serial_id] = {
            "incoming_university": {
                "code": incoming_university.get_code(),
                "name": incoming_university.get_name()
            },
            "incoming_serial_id": incoming_serial_id,
            "incoming_referrer": incoming_referrer,
            "internal_referrer": internal_referrer,
            "exchange_start_period": date.today().isoformat()
        }

    def pass_exam(self, student: Student, results: ExamResult):
        """
            Registra il superamento di un esame da parte dello studente.
        """
        serial_id = f"{student.get_code():03d}#{self._code:03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        
        if serial_id not in data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        if "exams" not in data[serial_id]:
            data[serial_id]["exams"] = {}

        data[serial_id]["exams"][results["name"]] = results

        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

    def pass_activity(self, student: Student, results: ActivityResult):
        """
            Registra il superamento di un'attività da parte dello studente.
        """
        serial_id = f"{student.get_code():03d}#{self._code:03d}"
        json_path = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, f"uni_{self._name}.json")
        with open(json_path, "r") as f:
            data = json.load(f)
        
        if serial_id not in data:
            raise ValueError(f" [{self._name}] Lo studente {student.get_code()} non è iscritto all'università.")
        
        if "activities" not in data[serial_id]:
            data[serial_id]["activities"] = {}
        
        data[serial_id]["activities"][results["name"]] = results
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)        