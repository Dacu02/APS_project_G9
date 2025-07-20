

import json
import os
from actors import Student
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from constants import DATA_DIRECTORY, STUDENTS_FOLDER


def crea_studente(args:list[str]=[]):
    students = lettura_dati()[0]
    code = read_code("Inserisci il codice dello studente: ", args[0] if len(args) > 0 else None)
    while code in students:
        print("Lo studente esiste già.")
        code = read_code("Inserisci il codice dello studente: ")
    if len(args) > 1:
        name = args[1]
    else:
        name = input("Inserisci il nome dello studente: ")

    if len(args) > 2:
        surname = args[2]
    else:
        surname = input("Inserisci il cognome dello studente: ")

    print("Studente creato con successo.")
    student = Student(name, surname, code)
    students[code] = student
    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump({code: student.save_on_json() for code, student in students.items()}, f, indent=4)
