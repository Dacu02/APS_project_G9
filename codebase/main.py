import time
import os
import json

from actors.Student import Student
from actors.University import University
from actors.CA import CA
from blockchain.Blockchain import Blockchain
from blockchain.Smart_Contract import Smart_Contract
from blockchain.MerkleTree import MerkleTree
from communication.Parametric_Symmetric_Scheme import Parametric_Symmetric_Scheme
from communication.Message import Message
from communication.Certificate import Certificate
from communication.Asymmetric_Scheme import Asymmetric_Scheme
from communication.Symmetric_Scheme import Symmetric_Scheme
from communication.Parametric_Asymmetric_Scheme import Parametric_Asymmetric_Scheme
from constants import BLOCKCHAIN_FOLDER, BLOCKCHAIN_HASH_ALGORITHM, DATA_DIRECTORY, STUDENTS_FOLDER, UNIVERSITIES_FOLDER, Activity, ActivityResult, CAs_FOLDER, RANDOM_NUMBER_MAX, MAXIMUM_TIMESTAMP_DIFFERENCE, Credential, ExamResult, StudyPlan, stringify_credential_dicts
import sys
import secrets
data_dir = os.path.join(os.getcwd(), DATA_DIRECTORY)
def crea_blochcain()-> tuple[Blockchain, Smart_Contract]:
    """
        Il seguente algoritmo crea la struttura della blockchain e istanzia uno smart contract, col quale le università possono comunicare
        Si presume che tutte le università siano a conoscenza della chiave pubblica dello smart contract, e che a sua volta lo smart contract sia a conoscenza
        di tutte le chiavi pubbliche delle università a cui è permesso manipolare la blockchain.
    """

    if not os.path.exists(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER)):
        os.makedirs(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER))
    if not os.path.exists(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json")):
        blockchain = Blockchain()
        smart_contract = Smart_Contract(blockchain, Parametric_Asymmetric_Scheme(), None)
        with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
            data = {
                "blockchain": blockchain.save_on_json(),
                "smart_contract": smart_contract.save_on_json()
            }
            json.dump(data, f, indent=4)
    else:
        with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'r') as f:
            blockchain_data = json.load(f)
            blockchain = Blockchain.load_from_json(blockchain_data["blockchain"])
            smart_contract = Smart_Contract.load_from_json(blockchain_data["smart_contract"])
        smart_contract._link_blockchain(blockchain) # Perdita del riferimento dopo lettura
    return blockchain, smart_contract



def lettura_dati() -> tuple[dict, dict, dict, dict, Blockchain, Smart_Contract]:
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
        private_uni_file = os.path.join(data_dir, UNIVERSITIES_FOLDER, "uni_.json")
        if os.path.exists(private_uni_file):
            with open(private_uni_file, 'r') as f_priv:
                private_universities = json.load(f_priv)
                universities.update(private_universities)
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

    return students, universities, CAs, configurazione, *crea_blochcain()

def immatricola(args:list[str]=[]):
    """
        Algoritmo di immatricolazione dello studente presso l'università. Lo studente deve fornire una password per autenticarsi in futuro.
        Tutti i messaggi in uscita dallo studente vengono cifrati con la chiave pubblica dell'università, quelli in entrata vengono solo firmati con la chiave privata dell'università.
        L'università deve essere certificata da una CA, e lo studente deve conoscere la chiave pubblica della CA per verificare il certificato dell'università.
        Args:
            - arg1: Codice dello studente
            - arg2: Codice dell'università
            - arg3: Nome della CA
            - arg4: Piano di studi scelto
            - arg5: Password scelta dallo studente

    """
    students, universities, CAs = lettura_dati()[0:3]
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
    public_key = ca.get_public_key()
    if public_key is None:
        raise ValueError(f"La CA {ca_name} non ha una chiave pubblica registrata.")

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
    i = 3
    if university.is_incoming_student(student):
        study_plan = "ext"
    else:
        study_plans = university.get_study_plans()
        if study_plans is None or len(study_plans) == 0:
            raise ValueError("L'università non ha piani di studio disponibili.")
        if len(args) > i:
            study_plan = args[i]
            i+=1
        else:
            study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")
        while study_plan not in study_plans:
            print(f"Il piano di studi {study_plan} non esiste nell'università {university_name}.")
            study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")

    student_initial_timestamp = time.time()
    random_number = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 999999 non basato su timestamp

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
    student.send(university, message, sign=False)
    #* 4 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di definire una password con la quale potrà autenticarsi successivamente
    #* Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    first_received_timestamp = received_data["timestamp"]
    # Controlla che la differenza del timestamp non superi la costante MAXIMUM_TIMESTAMP_DIFFERENCE
    if abs(time.time() - first_received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    uni_message = {
        "text": f"Benvenuto {received_data['name']} {received_data['surname']}, per favore fornisci una password per autenticarti in futuro, inoltre, ripeti il timestamp originale e l'attuale",
        "nonce": received_data["nonce"],
        "timestamp": time.time()
    }
    university.send(student, Message(json.dumps(uni_message)), encrypt=False, sign=True)

    #* 5 Lo studente riceve il messaggio e procede a definire una password
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())
    if received_data['nonce'] != random_number:
        raise ValueError("Il nonce non corrisponde a quello inviato, possibile replay attack.")
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    if len(args) > i:
        password = args[i]
        i+=1
    else:
        password = input("Inserisci una password per autenticarti all'università: ")
    while not password:
        print("La password non può essere vuota.")
        password = input("Inserisci una password per autenticarti all'università: ")
    student.set_password(password, university) # Lo studente si ricorderà la password per usi futuri (viene salvata in student.json in chiaro a scopo didattico)
    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump({code: s.save_on_json() for code, s in students.items()}, f, indent=4)
    #TODO Ricorda di scrivere la password in student.json

    password_message = {
        "password": password,
        "timestamp": time.time(),
        "nonce": student_initial_timestamp,
        "text": "Password di immatricolazione"
    }

    student.send(university, Message(json.dumps(password_message)), sign=False)
    #* 6 L'università riceve la password e la salva nel proprio database, immatricolando lo studente
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['nonce']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    if received_timestamp != first_received_timestamp:
        raise ValueError("Il timestamp ricevuto non corrisponde a quello originale, possibile replay attack.")

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
    university = University(name, code, BLOCKCHAIN_HASH_ALGORITHM())
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

    #* La CA genera una coppia di chiavi per sé e per i certificati
    scheme = Parametric_Asymmetric_Scheme()
    ca.add_key(ca, scheme)

    with open(os.path.join(data_dir, CAs_FOLDER, "CAs.json"), 'w') as f:
        json.dump({name: ca.save_on_json() for name, ca in CAs.items()}, f, indent=4)



def pulizia():
    if os.path.exists(DATA_DIRECTORY):
        for filename in os.listdir(DATA_DIRECTORY):
            file_path = os.path.join(DATA_DIRECTORY, filename)
            for subdir, _, files in os.walk(file_path):
                for file in files:
                    file_to_remove = os.path.join(subdir, file)
                    if os.path.isfile(file_to_remove):
                        os.remove(file_to_remove)
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

    scheme: Asymmetric_Scheme = Parametric_Asymmetric_Scheme()
    public_key = scheme.share_public_key()
    university.add_key(university, scheme)
    university.add_key(ca, ca.get_public_key()) 



    # Si immagina che l'università conosca già la CA sulla quale vuole certificare
    # la chiave pubblica e che comunichi attraverso altri mezzi alternativi sicuri


    #* 2 L'università chiede alla CA di certificare la propria chiave pubblica
    cert = ca.register_user_public_key(university, public_key)
    ca.add_key(university, public_key)
    
    if cert is None:
        raise ValueError(f"La CA {ca_name} non ha potuto certificare l'università {university_code}.")
    
    #* 3 La CA restituisce il certificato all'università
    certificate = ca.get_user_certificate(university)
    if certificate is None:
        raise ValueError(f"La CA {ca_name} non ha emesso correttamente il certificato per l'università {university_code}.")

    ca.send(university, certificate, encrypt=False)

    print(f"L'università {university.get_name()} è stata certificata con successo dalla CA {ca.get_code()}.")

    # Salva le chiavi aggiornate della CA e dell'università nei rispettivi file JSON
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump({code: uni.save_on_json() for code, uni in universities.items()}, f, indent=4)
    with open(os.path.join(data_dir, CAs_FOLDER, "CAs.json"), 'w') as f:
        json.dump({name: ca_obj.save_on_json() for name, ca_obj in CAs.items()}, f, indent=4)

def autenticazione(args:list[str]=[]):
    """
        Funzione per autenticare uno studente.
    """
    students, universities = lettura_dati()[0:2]

    university_code = read_code("Inserisci il codice dell'università ospitante: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università ospitante non esiste.")
        university_code = read_code("Inserisci il codice dell'università ospitante: ")

    student_code = read_code("Inserisci il codice dello studente: ", args[1] if len(args) > 1 else None)
    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")

    if len(args) > 2:
        password = args[2]
    else:
        password = input("Inserisci la password dello studente: ")
    while not password:
        print("La password non può essere vuota.")
        password = input("Inserisci la password dello studente: ")
    print(f"Password inserita per lo studente {student_code}: {password}")

    student:Student = students[student_code]
    university:University = universities[university_code]

    student_initial_timestamp = time.time()
    random_number = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 999999 non basato su timestamp
    #* 1 Lo studente invia un messaggio all'università con il proprio nome, cognome, codice, timestamp e un numero casuale
    message_data = {
        "name": student.get_name(),
        "surname": student.get_surname(),
        "code": student.get_code(),
        "timestamp": student_initial_timestamp,
        "text": "Richiesta di autenticazione",
        "nonce": random_number
    }

    message = Message(json.dumps(message_data))
    student.send(university, message, sign=False)
    #* 2 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di inserire la password per autenticarsi
    #* Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    first_received_timestamp = received_data['timestamp']
    if abs(time.time() - first_received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    received_nonce_challenge = received_data["nonce"]
    uni_message = {
        "text": f"Benvenuto {received_data['name']} {received_data['surname']}, per favore fornisci una password per autenticarti, inoltre, ripeti il timestamp originale e l'attuale",
        "nonce": received_data["timestamp"],
        "timestamp": time.time()
    }
    university.send(student, Message(json.dumps(uni_message)), encrypt=False, sign=True)

    #* 3 Lo studente riceve il messaggio e procede a inserire la password
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    if received_data['nonce'] != first_received_timestamp:
        raise ValueError("Il timestamp del messaggio dell'università non corrisponde a quello originale, possibile replay attack.")


    student_scheme = Parametric_Symmetric_Scheme()
    password_message = {
        "password": student.get_password(university),
        "timestamp": time.time(),
        "nonce": random_number,
        "text": "Password di autenticazione",
        # "scheme": student_scheme.save_on_json()
    }
    student.send(university, Message(json.dumps(password_message)), sign=False)
    # student.add_key(university, student_scheme)
    #* 4 L'università riceve la password e la verifica confrontandola con quella salvata nel proprio database
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    if received_data['nonce'] != received_nonce_challenge:
        raise ValueError("Il numero casuale del messaggio dello studente non corrisponde a quello originale, possibile replay attack.")
    check = university.check_password(student, received_data["password"])
    if not check:
        raise ValueError("Password errata, impossibile autenticare lo studente.")
    print(f"Autenticazione dello studente {student.get_name()} {student.get_surname()} ({student.get_code()}) avvenuta con successo.")
    
    #* 5 L'università risponde allo studente con un messaggio di autenticazione avvenuta con successo con attraverso la nuova chiave
    auth_message = {
        "text": f"Autenticazione avvenuta con successo {student.get_name()} {student.get_surname()} ({student.get_code()}). Inviami uno schema simmetrico casuale a partire dal nonce inviato",
        "timestamp": time.time(),
    }
    
    # university.add_key(student, uni_scheme)
    university.send(student, Message(json.dumps(auth_message)), encrypt=False, sign=True)
    print("Lo studente si è autenticato con successo, comunicazione cifrata da stabilire.")


    # Comunicazione delle componenti della chiave TCP style
    sender_k = received_nonce_challenge
    receiver_k = received_nonce_challenge
    sender_data = student_scheme.save_on_json()
    receiver_data = {}

    for key, value in sender_data.items():
        data_message = {
            "field": key,
            "value": value,
            "timestamp": time.time(),
            "nonce": sender_k
        }
        student.send(university, Message(json.dumps(data_message)), encrypt=True, sign=False)

        received_data = university.get_last_message()
        received_data = json.loads(received_data.get_content())

        if abs(time.time() - received_data['timestamp']) > MAXIMUM_TIMESTAMP_DIFFERENCE:
            raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

        if received_data['nonce'] != receiver_k:
            raise ValueError("Il numero di pacchetto del messaggio dello studente non corrisponde a quello originale, possibile replay attack.")


        received_key = received_data['field']
        received_value = received_data['value']
        receiver_data[received_key] = received_value

        response_message = {
            "nonce": receiver_k,
            "timestamp": time.time(),
        }
        university.send(student, Message(json.dumps(response_message)), encrypt=False, sign=True)

        received_data = student.get_last_message()
        received_data = json.loads(received_data.get_content())

        if received_data['nonce'] != sender_k:
            raise ValueError("Il numero di pacchetto del messaggio dello studente non corrisponde a quello originale, possibile replay attack.")
        
        if abs(time.time() - received_data['timestamp']) > MAXIMUM_TIMESTAMP_DIFFERENCE:
            raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

        sender_k += 1
        receiver_k += 1

    uni_scheme = Parametric_Symmetric_Scheme.load_from_json(receiver_data)
    student.add_key(university, uni_scheme) 
    university.add_key(student, uni_scheme) 
    print(f"Chiave simmetrica condivisa tra lo studente {student.get_name()} e l'università {university.get_name()} stabilita con successo.")

    # Invia un messaggio di test cifrato con il nuovo schema simmetrico
    test_message = {
        "text": "Test della comunicazione cifrata con il nuovo schema simmetrico.",
        "timestamp": time.time()
    }
    university.send(student, Message(json.dumps(test_message)), encrypt=True, sign=True)
    print("Messaggio di test cifrato inviato dallo studente all'università.")

    # Lo studente riceve e decifra il messaggio di test
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())

    # Salva le nuove chiavi simmetriche nei rispettivi file JSON

    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'r') as f:
        universities_data = json.load(f)    

    students_data[student_code] = student.save_on_json()
    universities_data[university_code] = university.save_on_json()

    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump(universities_data, f, indent=4)

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

    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'r') as f:
        universities_data = json.load(f)    

    # Lo studente rimuove la chiave dell'università dal proprio database e riprende quella pubblica
    # Per comodità si prende la precedente chiave pubblica dell'università
    previous_public_key = university._keys[university.get_code()].share_public_key()  # type: ignore
    student.add_key(university, previous_public_key)


    students_data[student_code] = student.save_on_json()
    universities_data[university_code] = university.save_on_json()


    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)
    with open(os.path.join(data_dir, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump(universities_data, f, indent=4)



def domanda_mobilita(args:list[str]=[]):
    """
        Funzione per inviare una domanda di mobilità dello studente.
        Lo studente deve essere autenticato presso l'università ospitante.
    """
    students, universities = lettura_dati()[0:2]

    university_code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università ospitante non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")
    
    destination_university_code = read_code("Inserisci il codice dell'università ospitante: ", args[1] if len(args) > 1 else None)
    while destination_university_code not in universities:
        print("L'università ospitante non esiste.")
        destination_university_code = read_code("Inserisci il codice dell'università ospitante: ")

    student_code = read_code("Inserisci il codice dello studente: ", args[2] if len(args) > 2 else None)
    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")

    autenticazione([university_code, student_code] + args[3:])  # Assicura che lo studente sia autenticato prima di inviare la domanda
    students, universities = lettura_dati()[0:2]
    student:Student = students[student_code]
    university:University = universities[university_code]
    initial_nonce = secrets.randbelow(RANDOM_NUMBER_MAX)

    i = 4
    study_plan:StudyPlan = []
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
        raise ValueError("Il piano di studi non può essere vuoto.")

    # Prendi in ingresso una lista di attività da aggiungere al piano di studi per la mobilità
    activities:list[Activity] = []
    while True:
        act_name = input("Inserisci il nome dell'attività (o premi invio per terminare): ") if len(args) <= i else args[i]
        i+=1
        if not act_name:
            break
        act_cfu = input("Inserisci il numero di CFU dell'attività: ") if len(args) <= i else args[i]
        i+=1
        while not act_cfu.isdigit():    
            print("Il numero di CFU deve essere un numero.")
            act_cfu = input("Inserisci il numero di CFU dell'attività: ")
        activities.append({"name": act_name, "cfus": int(act_cfu)})
    # Aggiungi le attività al piano di studi

    #* 1 Lo studente invia la domanda di mobilità all'università
    request_message = {
        "timestamp": time.time(),
        # "text": "Richiesta di mobilità",
        "nonce": initial_nonce,
        "destination_university": destination_university_code,
        "study_plan": study_plan,
        "activities": activities
    }

    if isinstance(student._keys[university.get_code()], Asymmetric_Scheme):
        raise ValueError("Lo studente non ha una chiave simmetrica condivisa con l'università, impossibile inviare la domanda di mobilità.")

    request_message = Message(json.dumps(request_message))
    student.send(university, request_message, sign=True)

    #* 2 L'università riceve la domanda 
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_nonce = received_data['nonce']
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    destination_university = received_data['destination_university']
    dest_uni:University = universities[destination_university]
    if len(args) > i:
        internal_ref = args[i]
        i+=1
    else:
        internal_ref = input("Inserisci il nome e cognome del referente interno dell'università: ")
    while not internal_ref.strip():
        internal_ref = input("Inserisci il nome e cognome del referente interno dell'università: ")

    #* 3 L'unversità contatta l'università ospitante e chiede se è possbile stringere l'accordo di mobilità, per fare ciò deve contattare una CA ed ottenerne la chiave pubblica
    #! Si presume che questa CA contenga entrambi i certificati
    CAs = lettura_dati()[2]
    if len(args) > i:
        ca_name = args[i]
        i+=1
    else:
        ca_name = input("Inserisci il nome della CA: ")
    while ca_name not in CAs:
        print("La CA non esiste.")
        ca_name = input("Inserisci il nome della CA: ")

    ca:CA = CAs[ca_name]


    cert = ca.get_user_certificate(dest_uni)
    if not cert:
        raise ValueError(f"La CA {ca_name} non ha un certificato registrato per l'università {destination_university}.")
    university.add_key(dest_uni, cert.read_key())


    cert = ca.get_user_certificate(university)
    if not cert:
        raise ValueError(f"La CA {ca_name} non ha un certificato registrato per l'università {university}.")
    dest_uni.add_key(university, cert.read_key())

    plan_tuples: list[tuple[str, int]] = [(ex["name"], ex["cfus"]) for ex in received_data["study_plan"]]
    activities_tuples: list[tuple[str, int]] = [(act["name"], act["cfus"]) for act in received_data["activities"]]


    check_plan_availability = {
        "timestamp": time.time(),
        'SP': plan_tuples,
        'ACT': activities_tuples,
        # "text": "Verifica disponibilità piano di studi per la mobilità",
        "internal_ref": internal_ref,
    }

    check_plan_availability = Message(json.dumps(check_plan_availability))
    university.send(dest_uni, check_plan_availability)

    #* 4 L'universitò ospitante riceve la richiesta di verifica della mobilità
    received_message = dest_uni.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    received_tuples_study_plan = received_data['SP']
    received_tuples_activities = received_data['ACT']

    received_study_plan = []
    received_activities = []
    for tupl in received_tuples_study_plan:
        received_study_plan.append({"name":tupl[0], "cfus": tupl[1]})
    
    for tupl in received_tuples_activities:
        received_activities.append({"name":tupl[0], "cfus": tupl[1]})

    received_ref = received_data["internal_ref"]

    response = True
    for course in received_study_plan:
        if not dest_uni.check_exam_availability(course):
            response = False

    for activity in received_activities:
        if not dest_uni.check_activity_availability(activity):
            response = False

    response_message = {
        "timestamp": time.time(),
        "text": f"Piano di studi {'non' if not response else ''} e\' disponibile per la mobilita\'",
        "result": response
    }

    response_message = Message(json.dumps(response_message))
    dest_uni.send(university, response_message, sign=True)

    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())

    availability = received_data['result']

    print(f"Il piano di studi {'non' if not availability else ''} e\' disponibile per la mobilita\'.")
    uni_response = {
        "timestamp": time.time(),
        "text": f"Il piano di studi {'non' if not availability else ''} e\' disponibile per la mobilita\'.",
        "nonce": received_nonce,
    }
    university.send(student, Message(json.dumps(uni_response)), sign=True)

    logout([university.get_code(), student.get_code()])
    
    if not availability:
        return

    #* 5 Le università preparano le condizioni per l'accordo di mobilità
    university.agree_exchange_contract(student, dest_uni, received_study_plan, received_activities, internal_ref)

    if len(args) > i:
        external_ref = args[i]
        i += 1
    else:
        external_ref = input("Inserisci il nome e cognome del referente esterno dell'università ospitante: ")
    while not external_ref.strip():
        external_ref = input("Inserisci il nome e cognome del referente esterno dell'università ospitante: ")
    dest_uni.accept_incoming_exchange(student, university, f"{student.get_code()}#{university.get_code()}", received_ref, external_ref)

def emetti_credenziale(args:list[str]=[]):
    """
        Funzione per emettere una credenziale di uno studente in mobilità iscritto ad un'università ospitante.
    """
    students, universities, _, _, blockchain, smart_contract = lettura_dati()

    university_code = read_code("Inserisci il codice dell'università ospitante: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università ospitante non esiste.")
        university_code = read_code("Inserisci il codice dell'università ospitante: ")
    
    student_code = read_code("Inserisci il codice dello studente: ", args[1] if len(args) > 1 else None)
    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")

    autenticazione([university_code, student_code] + args[2:])  # Assicura che lo studente sia autenticato prima di emettere la credenziale
    students, universities = lettura_dati()[0:2]
    student:Student = students[student_code]
    university:University = universities[university_code]

    #* 1 Lo studente comunica la richiesta della credenziale
    initial_nonce = secrets.randbelow(RANDOM_NUMBER_MAX)
    credential_request = {
        "timestamp": time.time(),
        "nonce": initial_nonce,
        "text": "Richiesta di credenziale",
    }
    request_message = Message(json.dumps(credential_request))
    student.send(university, request_message, sign=True)

    #* 2 L'università riceve la richiesta di credenziale e la verifica
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    received_nonce = received_data['nonce']


    
    credential = university.get_student_credential(student)
    #! L'università deve procedere a salvare il Merkle Tree della credenziale all'interno della blockchain
    # Si presume che l'università conoscoa l'algoritmo di hashing della blockchain
    hashing_algorithm = blockchain.get_hashing_algorithm()
    if hashing_algorithm is None:
        raise ValueError("L'algoritmo di hashing della blockchain non è stato definito.")
    stringified_credential = stringify_credential_dicts(credential)
    merkle_leafs = [hashing_algorithm.hash(data) for data in stringified_credential]
    received_nonce = received_data['nonce']
    blockchain_request = {
        "timestamp": time.time(),
        "leafs": merkle_leafs,
        "text": "Richiesta di certificazione credenziale nella blockchain",
    }
    
    request_message = Message(json.dumps(blockchain_request))

    # Si presume che le università conoscano già la chiave pubblica dello smart contract
    university.add_key(smart_contract, smart_contract.get_public_key())
    smart_contract.register_university(university, university._keys[university.get_code()].share_public_key()) # type: ignore #TODO Revisita

    university.send(smart_contract, request_message, encrypt=False, sign=True)

    received_data = smart_contract.get_last_message().get_content()
    received_data = json.loads(received_data)
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    
    if smart_contract.is_blacklisted(university):
        raise ValueError("L'università è stata inserita nella blacklist dello smart contract, impossibile procedere con la certificazione della credenziale.")
    
    #* 4 Lo smart contract verifica la richiesta e costruisce il merkle_tree
    mt = MerkleTree(merkle_leafs, hashing_algorithm)
    credential_ID = smart_contract.certificate_credential_MerkleTree(mt, university)


    #* 5 Lo smart contract risponde all'università con l'ID della credenziale
    response_message = {
        "timestamp": time.time(),
        "credential_ID": credential_ID,
        "text": "Credenziale certificata con successo nella blockchain"
    }
    response_message = Message(json.dumps(response_message))
    smart_contract.send(university, response_message, sign=True)
    
    
    #* 6 L'università risponde allo studente con l'ID della credenziale
    received_data = university.get_last_message().get_content()
    received_data = json.loads(received_data)
    received_timestamp = received_data['timestamp']
    received_credential_id = received_data["credential_ID"]
    university.set_credential_id(student, received_credential_id)
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")


    credential_message = {
        "timestamp": time.time(),
        "credential": credential,
        "credential_ID": received_credential_id,
        "nonce": received_nonce,
    }

    credential_message = Message(json.dumps(credential_message))
    university.send(student, credential_message, sign=True)

    #* 7 Lo studente riceve la credenziale e la salva localmente
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    if received_data['nonce'] != initial_nonce:
        raise ValueError("Il nonce ricevuto non corrisponde a quello inviato.")

    received_credential = received_data["credential"]
    student.save_credential(received_credential, credential_ID)
    # Lo studente salva la credenziale in locale
    logout([university_code, student_code])  # Rimuove le chiavi dello studente dall'università e viceversa

    with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
        data = {
            "blockchain": blockchain.save_on_json(),
            "smart_contract": smart_contract.save_on_json()
        }
        json.dump(data, f, indent=4)

    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)
    students_data[student_code] = student.save_on_json()
    with open(os.path.join(data_dir, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)

    
def divulga_credenziale(credenziale:Credential, args:list[str]=[]) -> Credential:
    print(" *** Divulgazione Selettiva della Credenziale *** ")
    lista_esami = {exam["name"]: exam for exam in credenziale["exams_results"]}
    lista_attivita = {activity["name"]: activity for activity in credenziale["activities_results"]}


    print("Esami disponibili: ", f" {', '.join(lista_esami.keys())}")
    print("Attività disponibili: ", f" {', '.join(lista_attivita.keys())}")
    i = 0
    if len(args) > i:
        action = args[i]
        i+=1
    else:
        action = input("Inserisci E per rimuovere un esame, oppure A per rimuovere una attività, o premi invio per continuare: ")
    while action:
        if action.lower() == "e":
            if len(args) > i:
                esame = args[i]
                i+=1
            else:
                esame = input("Inserisci il nome dell'esame da rimuovere: ")
            if esame in lista_esami:
                del lista_esami[esame]
                print(f"Esame {esame} rimosso.")
            else:
                print(f"Esame {esame} non trovato.")
        elif action.lower() == "a":
            if len(args) > i:
                attivita = args[i]
                i+=1
            attivita = input("Inserisci il nome dell'attività da rimuovere: ")
            if attivita in lista_attivita:
                del lista_attivita[attivita]
                print(f"Attività {attivita} rimossa.")
            else:
                print(f"Attività {attivita} non trovata.")
        else:
            print("Azione non valida, riprova.")
        if len(args) > i:
            action = args[i]
            i+=1
        else:
            action = input("Inserisci E per rimuovere un esame, oppure A per rimuovere una attività, o premi invio per continuare: ")

    #* Lo studente seleziona gli esami e le attività da rimuovere dalla credenziale

    credenziale["exams_results"] = list(lista_esami.values())
    credenziale["activities_results"] = list(lista_attivita.values())
    
    return credenziale

def presenta_credenziale(args:list[str]=[]):
    students, universities, _, _, blockchain, smart_contract = lettura_dati()

    student_code = read_code("Inserisci il codice dello studente: ", args[0] if len(args) > 0 else None)
    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")

    university_code = read_code("Inserisci il codice dell'università: ", args[1] if len(args) > 1 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    student: Student = students[student_code]
    university: University = universities[university_code]


    credential, credential_ID = student.get_credential_data()

    autenticazione([university_code, student_code] + args[2:])  # Assicura che lo studente sia autenticato prima di validare la credenziale
    students, universities = lettura_dati()[0:2]
    student: Student = students[student_code]
    university: University = universities[university_code]

    #* 1 Lo studente effettua la divulgazione selettiva della propria credenziale
    new_credential = divulga_credenziale(credential, args[3:]) if len(args) > 3 else divulga_credenziale(credential)

    #* 2 Lo studente invia la richiesta di validazione della credenziale, e la credenziale, all'università
    initial_nonce = secrets.randbelow(RANDOM_NUMBER_MAX)

    validation_message = {
        "timestamp": time.time(),
        "nonce": initial_nonce,
        "text": "Richiesta di validazione della credenziale",
        "credential": new_credential,
        "credential_ID": credential_ID
    }

    message = Message(json.dumps(validation_message))
    student.send(university, message, sign=True)

    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_credential = received_data["credential"]
    received_credential_id = received_data["credential_ID"]
    received_nonce = received_data["nonce"]
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    #* 3 L'università verifica la credenziale e poi controlla la certificazione sulla blockchain
    if not university.check_matching(student, received_credential):
        raise ValueError("La credenziale non è valida.")

    hashing_algorithm = blockchain.get_hashing_algorithm()
    merkle_leafs = [hashing_algorithm.hash(data) for data in stringify_credential_dicts(received_credential)]

    request_certification_validation = {
        "timestamp": time.time(),
        "text": "Richiesta di validazione della certificazione",
        "credential": merkle_leafs,
        "credential_ID": received_credential_id,
    }

    request_message = Message(json.dumps(request_certification_validation))
    # Si presume che le università conoscano già la chiave pubblica dello smart contract
    university.add_key(smart_contract, smart_contract.get_public_key())
    smart_contract.register_university(university, university._keys[university.get_code()].share_public_key()) # type: ignore #TODO Revisita
    university.send(smart_contract, request_message, encrypt=False, sign=True)


    received_message = smart_contract.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    received_leafs = received_data["credential"]
    received_ID = received_data["credential_ID"]
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    if smart_contract.is_blacklisted(university):
        raise ValueError("L'università è stata inserita nella blacklist dello smart contract, impossibile procedere con la validazione della credenziale.")

    validation_results = smart_contract.validate_credential_MerkleTreeLeafs(received_leafs, received_ID)

    #* 4 Lo smart contract risponde all'università con i risultati della validazione
    response_message = {
        "timestamp": time.time(),
        "validation_results": validation_results,
        "credential_ID": received_ID,
    }
    smart_contract.send(university, Message(json.dumps(response_message)), sign=True)

    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    received_id = received_data["credential_ID"]
    if received_id != received_credential_id:
        raise ValueError("L'ID della credenziale ricevuto non corrisponde a quello inviato.")
    
    validation_results = received_data["validation_results"]

    if validation_results:
        university.set_credential(student, received_credential, received_credential_id)  # Salva la credenziale validata nello studente

    #* 5 L'università risponde allo studente con i risultati della validazione
    validation_message = {
        "timestamp": time.time(),
        "nonce": received_nonce,
        "text": "Risultati della validazione della credenziale",
        "validation_results": validation_results,
        "credential_ID": received_id
    }

    university.send(student, Message(json.dumps(validation_message)), sign=True)

    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())

    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    if received_data['nonce'] != initial_nonce:
        raise ValueError("Il nonce ricevuto non corrisponde a quello inviato.")

    if received_data["credential_ID"] != credential_ID:
        raise ValueError("L'ID della credenziale ricevuto non corrisponde a quello inviato.")
    
    validation_results = received_data["validation_results"]
    logout([university_code, student_code])  # Rimuove le chiavi dello studente dall'università e viceversa

# ALGORITMI DI SIMULAZIONE DEGLI ATTACCHI

# FUNZIONI PER TESTING

def _registra_esame(cod_uni:str, cod_stud:str, exam_res:ExamResult):
    students = lettura_dati()[0]
    universities = lettura_dati()[1]

    cod_stud = read_code("Inserisci il codice dello studente: ", cod_stud)
    cod_uni = read_code("Inserisci il codice dello studente: ", cod_uni)

    if cod_uni not in universities.keys():
        raise ValueError("Università non trovata")

    if cod_stud not in students:
        raise ValueError("Studente non trovato")

    student: Student = students[cod_stud]
    university: University = universities[cod_uni]

    university.pass_exam(student, exam_res)

def _registra_attivita(cod_uni:str, cod_stud:str, act_res:ActivityResult):
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

if __name__ == "__main__":
    COD_UNI_INT = "001"
    COD_UNI_EXT = "002"
    COD_STUDENTE = "010"

    pulizia()
    crea_universita([COD_UNI_INT, "Unitest"])
    crea_CA(["CA1"])
    certifica_universita(["CA1", COD_UNI_INT])
    crea_piano_studi([COD_UNI_INT, "Informatica", "Programmazione", "6", "Sistemi Operativi", "6", "Analisi", "3", ""])
    crea_universita([COD_UNI_EXT, "UniExt"])
    crea_piano_studi([COD_UNI_EXT, "Matematica", "Fisica", "6", "Analisi", "6", ""])
    certifica_universita(["CA1", COD_UNI_EXT])
    crea_attivita([COD_UNI_INT, "Ricerca", "3"])
    crea_attivita([COD_UNI_EXT, "Ricerca", "3"])
    crea_studente([COD_STUDENTE, "Mario", "Rossi"])
    immatricola([COD_STUDENTE, COD_UNI_INT, "CA1", "Informatica", "TEST_PW"])

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

    domanda_mobilita([COD_UNI_INT, COD_UNI_EXT, COD_STUDENTE, "TEST_PW", "Analisi", "3", "Fisica", "3", "", "Ricerca", "3", "", "R_INT", "CA1", "R_EXT"])
    immatricola([COD_STUDENTE, COD_UNI_EXT, "CA1", "TEST_PW_EXT"])

    _registra_esame(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Fisica",
        "grade": 27,
        "lodging": False,
        "date": "2023-07-01",
        "prof": "Prof.ssa Verdi",
        "study_plan_name": "Matematica",
        "cfus": 3
    })

    _registra_esame(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Analisi",
        "grade": 29,
        "lodging": False,
        "date": "2023-07-15",
        "prof": "Prof. Neri",
        "study_plan_name": "Matematica",
        "cfus": 3
    })

    _registra_attivita(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Ricerca",
        "cfus": 3,
        "start_date": "2025-06-06",
        "end_date": "2025-07-06",
        "prof": "Prof. Rossi"
    })

    emetti_credenziale([COD_UNI_EXT, COD_STUDENTE, "TEST_PW_EXT"])
    presenta_credenziale([COD_STUDENTE, COD_UNI_INT, 'TEST_PW', 'E', "Fisica", ""])

    exit(0)

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
    elif command == "emetti_credenziale":
        emetti_credenziale(list(sys.argv[2:]))
    elif command == "presenta_credenziale":
        presenta_credenziale(list(sys.argv[2:]))
    elif command == "domanda_mobilita":
        domanda_mobilita(list(sys.argv[2:]))
    elif command == "logout":
        logout(list(sys.argv[2:]))
    else:
        print(f"Comando sconosciuto: {command}")

