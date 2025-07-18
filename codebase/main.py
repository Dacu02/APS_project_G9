from math import e
import time
import os
import json

from actors.Student import Student
from actors.University import University
from actors.CA import CA
from communication.Parametric_Symmetric_Scheme import Parametric_Symmetric_Scheme
from communication.Cipher_Block_Chaining import Cipher_Block_Chaining
from communication.Message import Message
from communication.Certificate import Certificate
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from communication.Symmetric_Scheme import Symmetric_Scheme
from constants import DATA_DIRECTORY, STUDENTS_FOLDER, UNIVERSITIES_FOLDER, Activity, CAs_FOLDER
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

def immatricola(args:list[str]=[]):
    students, universities, CAs, configurazione = lettura_dati()
    if len(args) > 0:
        student_name = args[0]
    else:
        student_name = input("Inserisci il nome dello studente: ")
    while student_name not in students:
        print("Lo studente non esiste.")
        student_name = input("Inserisci il nome dello studente: ")
    
    if len(args) > 1:
        university_name = args[1]
    else:
        university_name = input("Inserisci il nome dell'università: ")
    while university_name not in universities:
        print("L'università non esiste.")
        university_name = input("Inserisci il nome dell'università: ")

    
    if len(args) > 2:
        ca_name = args[2]
    else:
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
    if len(args) > 3:
        study_plan = args[3]
    else:
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
    
    if len(args) > 4:
        password = args[4]
    else:
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


def read_code(prompt: str, input_str:str|None=None) -> str:
    """
        Funzione per leggere un codice da input, con un prompt personalizzato.
        Ritorna il codice inserito.
    """
    if input_str:
        code = input_str
    else:
        code = input(prompt)
    while not code.isdigit() or len(code) != 3:
        print("Il codice deve essere un numero di 3 cifre.")
        code = input(prompt)
    return code


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
    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump({code: student.save_on_json() for code, student in students.items()}, f, indent=4)


def crea_universita(args:list[str]=[]):
    universities:dict[str, University] = lettura_dati()[1]
    code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while code in universities:
        print("L'università esiste già.")
        code = read_code("Inserisci il codice dell'università: ")
    
    if len(args) > 1:
        name = args[1]
    else:
        name = input("Inserisci il nome dell'università: ")
    
    print("Università creata con successo.")
    university = University(name, code)
    universities[code] = university
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump({code: university.save_on_json() for code, university in universities.items()}, f, indent=4)


def crea_piano_studi(args:list[str]=[]):
    universities:dict[str, University] = lettura_dati()[1]
    university_code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")
    
    if len(args) > 1:
        study_plan_name = args[1]
    else:
        study_plan_name = input("Inserisci il nome del piano di studi: ")

    while study_plan_name in universities[university_code].get_study_plans():
        print("Il piano di studi esiste già.")
        study_plan_name = input("Inserisci il nome del piano di studi: ")

    i = 2
    study_plan = []
    while True:
        if len(args) > i:
            course_name = args[i] # Esce in automatico se args[i] = ""
            i+=1
        else:
            course_name = input("Inserisci il nome del corso (o premi invio per terminare): ")
        if not course_name:
            break

        if len(args) > i:
            course_credit = args[i]
            i+=1
        else:
            course_credit = input("Inserisci il numero di crediti del corso: ")
        while not course_credit.isdigit():
            print("Il numero di crediti deve essere un numero.")
            course_credit = input("Inserisci il numero di crediti del corso: ")

        study_plan.append({"name": course_name, "cfus": int(course_credit)})
        
    if not study_plan:
        print("Piano di studi vuoto, non verrà creato.")
        return
    
    universities[university_code].add_study_plan(study_plan_name, study_plan)


def crea_attivita(args:list[str]=[]):
    universities:dict[str, University] = lettura_dati()[1]
    university_code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    if len(args) > 1:
        activity_name = args[1]
    else:
        activity_name = input("Inserisci il nome dell'attività: ")

    if len(args) > 2:
        activity_credit = args[2]
    else:
        activity_credit = input("Inserisci il numero di crediti dell'attività: ")
    while not activity_credit.isdigit():
        print("Il numero di crediti deve essere un numero.")
        activity_credit = input("Inserisci il numero di crediti dell'attività: ")

    activity:Activity = {"name": activity_name, "cfus": int(activity_credit)}

    universities[university_code].add_activity(activity)

def crea_CA(args:list[str]=[]):
    CAs = lettura_dati()[2]
    if len(args) > 0:
        name = args[0]
    else:
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


def certifica_universita(args:list[str]=[]):
    """
        Funzione per certificare un'università, richiede il nome della CA e dell'università.
        L'università genera una coppia di chiavi, e chiede alla CA di pubblicare la propria chiave pubblica attraverso un certificato.
    """
    CAs = lettura_dati()[2]
    universities = lettura_dati()[1]
    if len(args) > 0:
        ca_name = args[0]
    else:
        ca_name = input("Inserisci il nome della CA: ")
    while ca_name not in CAs:
        print("La CA non esiste.")
        ca_name = input("Inserisci il nome della CA: ")

    university_code = read_code("Inserisci il codice dell'università: ", args[1] if len(args) > 1 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    ca:CA = CAs[ca_name]
    university:University = universities[university_code]

    #* 1 L'università genera una coppia di chiavi
    # university.generate_key_pair() #TODO Definisci il metodo generate_key_pair  
    scheme: Asymmetric_Scheme = university._keys[self] # type: ignore #Todo ricorda di rimuovere questa riga quando implementi il metodo generate_key_pair
    #* 2 L'università chiede alla CA di certificare la propria chiave pubblica
    cert = ca.register_user_public_key(university, scheme)
    
    if cert is None:
        raise ValueError(f"La CA {ca_name} non ha potuto certificare l'università {university_code}.")
    
    #* 3 La CA restituisce il certificato all'università
    certificate = ca.get_user_certificate(university)
    if certificate is None:
        raise ValueError(f"La CA {ca_name} non ha emesso correttamente il certificato per l'università {university_code}.")

    # ca.send(university, certificate)
    university._receive(ca, certificate) 

    print(f"L'università {university.get_name()} è stata certificata con successo dalla CA {ca.get_code()}.")


if __name__ == "__main__":

    # Genera due utenti (studenti) e falli comunicare

    # Crea due studenti di esempio
    student1 = Student("Alice", "Rossi", "101")
    student2 = Student("Bob", "Bianchi", "102")


    # Crea uno schema simmetrico per cifrare il messaggio
    scheme:Symmetric_Scheme = Parametric_Symmetric_Scheme()
    student1.add_key(student2, scheme)
    student2.add_key(student1, Parametric_Symmetric_Scheme.load_from_json(scheme.save_on_json()))

    # Crea un messaggio da Alice a Bob
    message = Message("Ciao Bob, sono Alice!")
    student1.send(student2, message, sign=True)
    
    # Crea un messaggio di risposta da Bob ad Alice
    reply = Message("Ciao Alice, piacere di conoscerti!")
    student2.send(student1, reply, sign=True)
    exit()
    if len(sys.argv) < 2:

        print("Inserisci il nome di un algoritmo")
        command = input("Comando: ")
    else:
        command = sys.argv[1]

    if command == "pulizia":
        pulizia()
    elif command == "crea_studente":
        crea_studente(list(sys.argv[2:]))
    elif command == "crea_universita":
        crea_universita(list(sys.argv[2:]))
    elif command == "crea_piano_studi":
        crea_piano_studi(list(sys.argv[2:]))
    elif command == "crea_attivita":
        crea_attivita(list(sys.argv[2:]))
    elif command == "crea_CA":
        crea_CA(list(sys.argv[2:]))
    elif command == "immatricola":
        immatricola(list(sys.argv[2:]))
    elif command == "certifica_universita":
        certifica_universita(list(sys.argv[2:]))
    else:
        print(f"Comando sconosciuto: {command}")