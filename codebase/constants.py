from datetime import date
from typing import TypeAlias, TypedDict

from communication.Generic_Hash_Algorithm import Generic_Hash_Algorithm

DATA_DIRECTORY = "data"
STUDENTS_FOLDER = "students"
UNIVERSITIES_FOLDER = "universities"
CAs_FOLDER = "CAs"
KEY_LENGTH = 32  # Lunghezza della chiave in byte (256 bit)
IV_SIZE = 16 # 128 bit
MAC_SIZE = 32 #256 bit per HMAC-SHA256
BLOCKCHAIN_HASH_ALGORITHM = lambda : Generic_Hash_Algorithm("SHA256")
RANDOM_NUMBER_MAX = 10**6
MAXIMUM_TIMESTAMP_DIFFERENCE = 60  # Un minuto in secondi
EXCHANGE_DEFAULT_PERIOD_DAYS = 120 # 120 giorni di scambio predefiniti
CREDENTIAL_PERIOD_DAYS = 365 # 365 giorni di validità della credenziale

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
    type: str
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
            "type": activity["type"],
            "start_date": activity["start_date"],
            "end_date": activity["end_date"],
            "cfus": activity["cfus"],
            "prof": activity["prof"],
        } for activity in credential["activities_results"]
    ]

    return [str(data)] + [str(exam) for exam in exam_datas] + [str(activity) for activity in activities_data]