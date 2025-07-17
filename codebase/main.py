import time
import os
import json

from actors.Student import Student
from actors.University import University
from actors.CA import CA
from communication.User import User
from communication.Cipher_Block_Chaining import Cipher_Block_Chaining
from communication.Symmetric_Scheme import Symmetric_Scheme
from communication.Message import Message
from communication.Certificate import Certificate
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from constants import DATA_DIRECTORY, STUDENTS_FOLDER, UNIVERSITIES_FOLDER, Activity, CAs_FOLDER, StudyPlan
import sys
import secrets
data_dir = os.path.join(os.getcwd(), DATA_DIRECTORY)

def lettura_dati() -> tuple[dict, dict, dict, dict]:
    """
        L'algoritmo legge i dati e le configurazioni dai file JSON presenti nella cartella "data".
    """

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if not os.path.exists(os.path.join(data_dir, "config.json")):
        with open(os.path.join(data_dir, "config.json"), 'w') as f:
            configurazione = {}
            # Eventuale configurazioni da inizializzare
            json.dump(configurazione, f, indent=4)

    if not os.path.exists(os.path.join(data_dir, STUDENTS_FOLDER)):
        os.makedirs(os.path.join(data_dir, STUDENTS_FOLDER))
    if not os.path.exists(os.path.join(data_dir, STUDENTS_FOLDER, "students.json")):
        with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'w') as f:
            students = {}
            # Eventuale lista di studenti da inizializzare
            json.dump(students, f, indent=4)

    if not os.path.exists(os.path.join(data_dir, UNIVERSITIES_FOLDER)):
        os.makedirs(os.path.join(data_dir, UNIVERSITIES_FOLDER))
    if not os.path.exists(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json")):
        with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
            universities = {}
            json.dump(universities, f, indent=4)

    if not os.path.exists(os.path.join(data_dir, CAs_FOLDER)):
        os.makedirs(os.path.join(data_dir, CAs_FOLDER))
    if not os.path.exists(os.path.join(data_dir, CAs_FOLDER, "CAs.json")):
        with open(os.path.join(data_dir, CAs_FOLDER, "CAs.json"), 'w') as f:
            CAs = {}
            json.dump(CAs, f, indent=4)

    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students = json.load(f)
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'r') as f:
        universities = json.load(f)
    with open(os.path.join(data_dir, CAs_FOLDER, "CAs.json"), 'r') as f:
        CAs = json.load(f)
    with open(os.path.join(data_dir, "config.json"), 'r') as f:
        configurazione = json.load(f)

    for student_name, student_data in students.items():
        students[student_name] = Student.load_from_json(student_data)

    for university_name, university_data in universities.items():
        universities[university_name] = University.load_from_json(university_data)
    
    for ca_name, ca_data in CAs.items():
        CAs[ca_name] = CA.load_from_json(ca_data)

    return students, universities, CAs, configurazione

def immatricola():
    students, universities, CAs, configurazione = lettura_dati()
    student_name = input("Inserisci il nome dello studente: ")
    while student_name not in students:
        print("Lo studente non esiste.")
        student_name = input("Inserisci il nome dello studente: ")
    
    university_name = input("Inserisci il nome dell'università: ")
    while university_name not in universities:
        print("L'università non esiste.")
        university_name = input("Inserisci il nome dell'università: ")

    ca_name = input("Inserisci il nome della CA: ")
    while ca_name not in CAs:
        print("La CA non esiste.")
        ca_name = input("Inserisci il nome di una CA dove la chiave pubblica dell'università è registrata, o premi invio per prenderne una disponibile")

    if ca_name == "":
        print("TODO") #TODO Cerca una CA con un certificato valido per l'università
    
    student:Student = students[student_name]
    university:University = universities[university_name]
    ca:CA = CAs[ca_name]
    
    #* 1 Lo studente cerca la chiave pubblica dell'università dalla CA, ha prima bisogno della chiave pubblica della CA
    mex = ca.get_user_public_key(ca)
    if mex is None:
        raise ValueError(f"La CA {ca_name} non ha una chiave pubblica registrata.")

    public_key = mex[0].share_public_key() # Root CA
    if public_key is None:
        raise ValueError(f"La CA {ca_name} non ha una chiave pubblica registrata.")

    if not isinstance(public_key, Asymmetric_Scheme):
        raise TypeError(f"La chiave pubblica della CA deve essere di tipo Asymmetric_Scheme, ma è di tipo {type(public_key)}")
    
    #* 2 Lo studente utilizza la chiave pubblica della CA per verificare che certificato che riceve dalla CA sia valido
    uni_cert = ca.get_user_certificate(university)
    if uni_cert is None:
        raise ValueError(f"La CA {ca_name} non ha un certificato registrato per l'università {university_name}.")
    if not isinstance(uni_cert, Certificate):
        raise TypeError(f"Il certificato dell'università deve essere di tipo Certificate, ma è di tipo {type(uni_cert)}")
    
    if not public_key.verify(uni_cert):
        raise ValueError(f"Il certificato dell'università {university_name} non è valido: la firma non corrisponde.")
    print("Certificato dell'università verificato con successo.")
    uni_public_key = uni_cert.read_key()


    #* 3 Lo studente si salva la chiave pubblica dell'università e la utilizza per comunicare con essa
    student.add_key(university, uni_public_key)
    study_plans = university.get_study_plans()
    if study_plans is None or len(study_plans) == 0:
        raise ValueError("L'università non ha piani di studio disponibili.")
    study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")
    while study_plan not in study_plans:
        print(f"Il piano di studi {study_plan} non esiste nell'università {university_name}.")
        study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")

    student_initial_timestamp = time.time()
    random_number = secrets.randbelow(10**6)  # Numero casuale tra 0 e 999999 non basato su timestamp

    message_data = {
        "name": student.get_name(),
        "surname": student.get_surname(),
        "code": student.get_code(),
        "timestamp": student_initial_timestamp,
        "text": "Richiesta di immatricolazione",
        "study_plan": study_plan,
        # "email": "..." # Si potrebbe considerare in futuro l'utilizzo di una email come scenario 2FA
        "nonce": random_number
    }

    message = Message(json.dumps(message_data))
    student.send(university, message, sign=True)
    #* 4 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di definire una password con la quale potrà autenticarsi successivamente
    #* Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    uni_message = {
        "text": f"Benvenuto {message_data['name']} {message_data['surname']}, per favore fornisci una password per autenticarti in futuro, inoltre, ripeti il timestamp originale e l'attuale",
        "timestamp": message_data["timestamp"],
    }
    university.send(student, Message(json.dumps(uni_message)), encrypt=False, sign=True)

    #* 5 Lo studente riceve il messaggio e procede a definire una password
    if uni_message['timestamp'] != message_data['timestamp']:
        raise ValueError("Il timestamp del messaggio dell'università non corrisponde a quello originale, possibile replay attack.")
    
    password = input("Inserisci una password per autenticarti all'università: ")
    while not password:
        print("La password non può essere vuota.")
        password = input("Inserisci una password per autenticarti all'università: ")
    student.set_password(password, university) # Lo studente si ricorderà la password per usi futuri (viene salvata in student.json in chiaro a scopo didattico)
    #TODO Ricorda di scrivere la password in student.json

    password_message = {
        "password": password,
        "timestamp": time.time(),
        "nonce": random_number,
        "text": "Password di immatricolazione"
    }

    student.send(university, Message(json.dumps(password_message)), sign=True)
    #* 6 L'università riceve la password e la salva nel proprio database, immatricolando lo studente

    if password_message['nonce'] != random_number:
        raise ValueError("Il numero casuale del messaggio dello studente non corrisponde a quello originale, possibile replay attack.")

    university.enroll_student(student, password, study_plan)


def read_code(prompt: str) -> str:
    """
        Funzione per leggere un codice da input, con un prompt personalizzato.
        Ritorna il codice inserito.
    """
    code = input(prompt)
    while not code.isdigit() or len(code) != 3:
        print("Il codice deve essere un numero di 3 cifre.")
        code = input(prompt)
    return code


def crea_studente():
    students = lettura_dati()[0]
    code = read_code("Inserisci il codice dello studente: ")
    while code in students:
        print("Lo studente esiste già.")
        code = read_code("Inserisci il codice dello studente: ")
    name = input("Inserisci il nome dello studente: ")
    surname = input("Inserisci il cognome dello studente: ")

    print("Studente creato con successo.")
    student = Student(name, surname, code)
    students[code] = student
    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump({code: student.save_on_json() for code, student in students.items()}, f, indent=4)


def crea_universita():
    universities:dict[str, University] = lettura_dati()[1]
    code = read_code("Inserisci il codice dell'università: ")
    while code in universities:
        print("L'università esiste già.")
        code = read_code("Inserisci il codice dell'università: ")
    
    name = input("Inserisci il nome dell'università: ")
    
    print("Università creata con successo.")
    university = University(name, code)
    universities[code] = university
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump({code: university.save_on_json() for code, university in universities.items()}, f, indent=4)


def crea_piano_studi():
    universities:dict[str, University] = lettura_dati()[1]
    university_code = read_code("Inserisci il codice dell'università: ")
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")
    
    study_plan_name = input("Inserisci il nome del piano di studi: ")
    while study_plan_name in universities[university_code].get_study_plans():
        print("Il piano di studi esiste già.")
        study_plan_name = input("Inserisci il nome del piano di studi: ")

    study_plan = []
    while True:
        course_name = input("Inserisci il nome del corso (o premi invio per terminare): ")
        if not course_name:
            break
        course_credit = input("Inserisci il numero di crediti del corso: ")
        while not course_credit.isdigit():
            print("Il numero di crediti deve essere un numero.")
            course_credit = input("Inserisci il numero di crediti del corso: ")

        study_plan.append({"name": course_name, "cfus": int(course_credit)})
        
    if not study_plan:
        print("Piano di studi vuoto, non verrà creato.")
        return
    
    universities[university_code].add_study_plan(study_plan_name, study_plan)


def crea_attivita():
    universities:dict[str, University] = lettura_dati()[1]
    university_code = read_code("Inserisci il codice dell'università: ")
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    activity_name = input("Inserisci il nome dell'attività: ")
    activity_credit = input("Inserisci il numero di crediti dell'attività: ")
    while not activity_credit.isdigit():
        print("Il numero di crediti deve essere un numero.")
        activity_credit = input("Inserisci il numero di crediti dell'attività: ")

    activity:Activity = {"name": activity_name, "cfus": int(activity_credit)}

    universities[university_code].add_activity(activity)

def crea_CA():
    CAs = lettura_dati()[2]
    name = input("Inserisci il nome della CA: ")
    while name in CAs:
        print("La CA esiste già.")
        name = input("Inserisci il nome della CA: ")
    
    print("CA creata con successo.")
    ca = CA(name)
    CAs[name] = ca
    with open(os.path.join(data_dir, CAs_FOLDER, "CAs.json"), 'w') as f:
        json.dump({name: ca.save_on_json() for name, ca in CAs.items()}, f, indent=4)


def pulizia():
    if os.path.exists(DATA_DIRECTORY):
        for filename in os.listdir(DATA_DIRECTORY):
            file_path = os.path.join(DATA_DIRECTORY, filename)
            os.remove(file_path)
    else:
        os.makedirs(DATA_DIRECTORY)


def login_studente():
    students, universities, CAs, _ = lettura_dati()
    student_code = read_code("Inserisci il codice dello studente: ")
    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")

    university_code = read_code("Inserisci il codice dell'università: ")
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    ca_name = input("Inserisci il nome della CA: ")
    while ca_name not in CAs:
        print("La CA non esiste.")
        ca_name = input("Inserisci il nome della CA: ")

    print(f"Studente selezionato: {students[student_code].name} {students[student_code].surname}")
    print(f"Università selezionata: {universities[university_code].name}")
    print(f"CA selezionata: {CAs[ca_name].name}")

if __name__ == "__main__":
    
    
    scheme:Symmetric_Scheme = Cipher_Block_Chaining()
    userA = Student("Alice", "", "001")
    userB = Student("Bob", "", "002")
    userA.add_key(userB, scheme)
    userB.add_key(userA, scheme)
    userA.send(userB, Message("Ciao Bob! Come va?"))


    exit()
    if len(sys.argv) < 2:

        print("Inserisci il nome di un algoritmo")
        command = input("Comando: ")
    else:
        command = sys.argv[1]

    if command == "pulizia":
        pulizia()
    elif command == "crea_studente":
        crea_studente()
    elif command == "crea_universita":
        crea_universita()
    elif command == "crea_piano_studi":
        crea_piano_studi()
    elif command == "crea_attivita":
        crea_attivita()
    elif command == "crea_CA":
        crea_CA()
    elif command == "immatricola":
        immatricola()
    else:
        print(f"Comando sconosciuto: {command}")