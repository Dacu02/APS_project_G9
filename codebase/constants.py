from typing import TypeAlias, TypedDict
import os


from communication.Generic_Hash_Algorithm import Generic_Hash_Algorithm

DATA_DIRECTORY = os.path.join(os.path.dirname(__file__), "data")
STUDENTS_FOLDER = "students"
UNIVERSITIES_FOLDER = "universities"
BLOCKCHAIN_FOLDER = "blockchain"
EXPERIMENTS_FOLDER = "experiments"
CAs_FOLDER = "CAs"

SYMMETRIC_KEY_LENGTH = 32  # Lunghezza della chiave in byte
IV_SIZE = 16 # 128 bit
MAC_SIZE = 32 #256 bit per HMAC-SHA256

ASYMMETRIC_KEY_LENGTH = 256  # Lunghezza della chiave in byte

BLOCKCHAIN_HASH_ALGORITHM = lambda : Generic_Hash_Algorithm("SHA256")
RANDOM_NUMBER_MAX = 10**4 # Numero casuale tra 0 e 9999
MAXIMUM_TIMESTAMP_DIFFERENCE = 120  # Due minuti in secondi
EXCHANGE_DEFAULT_PERIOD_DAYS = 120 # 120 giorni di scambio predefiniti
CREDENTIAL_PERIOD_DAYS = 365 # 365 giorni di validità della credenziale
BLACKLIST_THRESHOLD = .25  # Soglia per considerare un'università nella blacklist (25% delle università)

PRINT_MAX_LENGTH = -1
DECORATION_CHARACTERS = 51  # Numero di caratteri per la decorazione nei messaggi

class Exam(TypedDict):
    """
        Rappresenta un esame nel piano di studi.
    """
    name: str
    cfus: int

class Activity(TypedDict):
    """
        Rappresenta un'attività nel piano di studi.
    """
    name: str
    cfus: int
    

StudyPlan: TypeAlias = list[Exam]

class ExamResult(TypedDict):
    """
        Rappresenta il risultato di un esame.
    """
    name:str
    grade:int|bool
    lodging:bool|None
    date:str
    prof:str
    study_plan_name:str
    cfus:int

class ActivityResult(TypedDict):
    """
        Rappresenta il risultato di un'attività.
    """
    name: str
    start_date: str
    end_date: str
    cfus: int
    prof: str



class Credential(TypedDict):
    """
        Rappresenta una credenziale fornita dall'università ospitante.
    """
    internal_serial_id: str
    external_serial_id: str
    name: str
    surname: str
    external_university: str
    external_university_code: str
    internal_referrer: str
    external_referrer: str
    emission_date: str
    expiration_date: str
    exchange_period_start: str
    exchange_period_end: str
    exams_results: list[ExamResult]
    activities_results: list[ActivityResult]

def stringify_credential_dicts(credential: Credential) -> list[str]:
    """
        Converte i dati della credenziale in una lista di stringhe per costruire successivamente un Merkle Tree o validarla.
        Parametri:
        - credential: La credenziale da cui costruire il Merkle Tree.
        Restituisce:
        - Una lista di stringhe contenente i dati della credenziale.
    """
    data = {
        "internal_serial_id": credential["internal_serial_id"],
        "external_serial_id": credential["external_serial_id"],
        "name": credential["name"],
        "surname": credential["surname"],
        "external_university": credential["external_university"],
        "external_university_code": credential["external_university_code"],
        "internal_referrer": credential["internal_referrer"],
        "external_referrer": credential["external_referrer"],
        "emission_date": str(credential["emission_date"]),
        "expiration_date": str(credential["expiration_date"]),
        "exchange_period_start": str(credential["exchange_period_start"]),
        "exchange_period_end": str(credential["exchange_period_end"]),
    }
    exam_datas = [
        {
            "name": exam["name"],
            "grade": exam["grade"],
            "lodging": exam["lodging"],
            "date": exam["date"],
            "prof": exam["prof"],
            "study_plan_name": exam["study_plan_name"],
            "cfus": exam["cfus"]
        } for exam in credential["exams_results"]
    ]
    activities_data = [
        {
            "name": activity["name"],
            "start_date": activity["start_date"],
            "end_date": activity["end_date"],
            "cfus": activity["cfus"],
            "prof": activity["prof"],
        } for activity in credential["activities_results"]
    ]

    return [str(data)] + [str(exam) for exam in exam_datas] + [str(activity) for activity in activities_data]


def _registra_esame(cod_uni:str, cod_stud:str, exam_res:ExamResult):
    from algorithms import lettura_dati, read_code
    from actors import Student, University

    students = lettura_dati()[0]
    universities = lettura_dati()[1]

    cod_stud = read_code("Inserisci il codice dello studente: ", cod_stud)
    cod_uni = read_code("Inserisci il codice dell'università: ", cod_uni)

    if cod_uni not in universities.keys():
        raise ValueError("Università non trovata")

    if cod_stud not in students:
        raise ValueError("Studente non trovato")

    student: Student = students[cod_stud]
    university: University = universities[cod_uni]

    university.pass_exam(student, exam_res)


def _registra_attivita(cod_uni:str, cod_stud:str, act_res:ActivityResult):
    from algorithms import lettura_dati, read_code
    from actors import Student, University
    students = lettura_dati()[0]
    universities = lettura_dati()[1]

    cod_stud = read_code("Inserisci il codice dello studente: ", cod_stud)
    cod_uni = read_code("Inserisci il codice dell'università: ", cod_uni)

    if cod_stud not in students:
        raise ValueError("Studente non trovato")

    if cod_uni not in universities:
        raise ValueError("Università non trovata")

    student: Student = students[cod_stud]
    university: University = universities[cod_uni]

    university.pass_activity(student, act_res)
