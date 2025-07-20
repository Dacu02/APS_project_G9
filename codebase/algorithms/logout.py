import json
import os
from actors import University
from actors.Student import Student
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from constants import DATA_DIRECTORY, STUDENTS_FOLDER, UNIVERSITIES_FOLDER


def logout(args:list[str]=[]):
    """
        Funzione per effettuare il logout dello studente.
        Rimuove le chiavi dello studente dall'università e viceversa.
    """
    students = lettura_dati()[0]
    universities = lettura_dati()[1]

    university_code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    student_code = read_code("Inserisci il codice dello studente: ", args[1] if len(args) > 1 else None)
    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")

    student:Student = students[student_code]
    university:University = universities[university_code]

    student.add_key(university, None)  # Rimuove dallo studente la chiave dell'università
    university.add_key(student, None)  # Rimuove dall'università la chiave dello studente

        # Salva le nuove chiavi simmetriche nei rispettivi file JSON

    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)
    with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'r') as f:
        universities_data = json.load(f)    

    # Lo studente rimuove la chiave dell'università dal proprio database e riprende quella pubblica
    # Per comodità si prende la precedente chiave pubblica dell'università
    previous_public_key = university._keys[university.get_code()].share_public_key()  # type: ignore
    student.add_key(university, previous_public_key)


    students_data[student_code] = student.save_on_json()
    universities_data[university_code] = university.save_on_json()


    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)
    with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump(universities_data, f, indent=4)