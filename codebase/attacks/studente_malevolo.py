
import json
import os
import sys

from actors.Student import Student
from algorithms import *
from constants import DATA_DIRECTORY, STUDENTS_FOLDER, ExamResult, _registra_attivita, _registra_esame

def _manipola_credenziale(student_code: str, esame_non_superato: ExamResult):
    students = lettura_dati()[0]

    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")
    student: Student = students[student_code]
    credenziale, ID = student.get_credential_data()
    lista_esami = {exam["name"]: exam for exam in credenziale["exams_results"]}

    print(f"Aggiunta di un esame non superato: {esame_non_superato['name']}")
    lista_esami[esame_non_superato["name"]] = esame_non_superato
    credenziale["exams_results"] = list(lista_esami.values())
    student.save_credential(credenziale, ID)

    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)

    students_data[student_code] = student.save_on_json()
    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)

def studente_malevolo():
    COD_UNI_INT = "001"
    COD_UNI_EXT = "002"
    COD_STUDENTE = "010"

    _CA = "CA1"
    pulizia()
    crea_CA([_CA])

    crea_universita([COD_UNI_INT, "UniInt"])
    certifica_universita([_CA, COD_UNI_INT])
    crea_piano_studi([COD_UNI_INT, "Informatica", "Programmazione", "6", "Sistemi Operativi", "6", "Analisi", "3", ""])
    crea_attivita([COD_UNI_INT, "Ricerca", "3"])

    crea_universita([COD_UNI_EXT, "UniExt"])
    certifica_universita([_CA, COD_UNI_EXT])
    crea_piano_studi([COD_UNI_EXT, "Matematica", "Fisica", "4", "Analisi", "4", ""])
    crea_attivita([COD_UNI_EXT, "Ricerca", "3"])
    crea_studente([COD_STUDENTE, "Mario", "Rossi"])


    immatricola([COD_STUDENTE, COD_UNI_INT, _CA, "Informatica", "TEST_PW"])

    _registra_esame(COD_UNI_INT, COD_STUDENTE, {
        "name":"Programmazione",
        "grade":28,
        "lodging":False,
        "date":"2023-05-15",
        "prof":"Prof. Rossi",
        "study_plan_name":"Informatica",
        "cfus":6
    })
    
    _registra_esame(COD_UNI_INT, COD_STUDENTE, {
        "name": "Sistemi Operativi",
        "grade": 30,
        "lodging": True,
        "date": "2023-06-10",
        "prof": "Prof. Bianchi",
        "study_plan_name": "Informatica",
        "cfus": 6
    })

    domanda_mobilita([COD_UNI_INT, COD_UNI_EXT, COD_STUDENTE, "TEST_PW", "Analisi", "3", "", "Ricerca", "3", "", "R_INT", _CA, "R_EXT"])

    immatricola([COD_STUDENTE, COD_UNI_EXT, _CA, "TEST_PW_EXT"])

    _registra_esame(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Fisica",
        "grade": 27,
        "lodging": False,
        "date": "2023-07-01",
        "prof": "Prof.ssa Verdi",
        "study_plan_name": "Matematica",
        "cfus": 4
    })

    esame_non_superato:ExamResult = {
        "name": "Analisi",
        "grade": 30,
        "lodging": True,
        "date": "2023-07-15",
        "prof": "Prof. Neri",
        "study_plan_name": "Matematica",
        "cfus": 4
    }
    
    # ! L'esame di Analisi non è stato superato, per cui non verrà registrato dall'università ospitante
    # _registra_esame(COD_UNI_EXT, COD_STUDENTE, {
    #     "name": "Analisi",
    #     "grade": 29,
    #     "lodging": False,
    #     "date": "2023-07-15",
    #     "prof": "Prof. Neri",
    #     "study_plan_name": "Matematica",
    #     "cfus": 4
    # })

    _registra_attivita(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Ricerca",
        "cfus": 3,
        "start_date": "2025-06-06",
        "end_date": "2025-07-06",
        "prof": "Prof. Rossi"
    })

    emetti_credenziale([COD_UNI_EXT, COD_STUDENTE, "TEST_PW_EXT"])

    _manipola_credenziale(COD_STUDENTE, esame_non_superato)

    presenta_credenziale([COD_STUDENTE, COD_UNI_INT, 'TEST_PW', 'E', "Fisica", ""])
    revoca_credenziale([COD_STUDENTE, COD_UNI_EXT])
    verifica_credenziale([COD_STUDENTE, COD_UNI_INT])