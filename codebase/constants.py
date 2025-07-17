from typing import TypeAlias, TypedDict

DATA_DIRECTORY = "data"
STUDENTS_FOLDER = "students"
UNIVERSITIES_FOLDER = "universities"
CAs_FOLDER = "CAs"
KEY_LENGTH = 32  # Lunghezza della chiave in byte (256 bit)
_IV_SIZE = 16 # 128 bit
_MAC_SIZE = 32 #256 bit per HMAC-SHA256


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
    prof_name:str
    prof_surname:str
    study_plan_name:str
    cfus:int

class ActivityResult(TypedDict):
    """
        Rappresenta un'attività nel piano di studi.
    """
    name: str
    type: str
    start_date: str
    end_date: str
    cfus: int
    prof_name: str
    prof_surname: str