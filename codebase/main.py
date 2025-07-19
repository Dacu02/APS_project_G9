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
from constants import BLOCKCHAIN_FOLDER, DATA_DIRECTORY, STUDENTS_FOLDER, UNIVERSITIES_FOLDER, Activity, CAs_FOLDER, RANDOM_NUMBER_MAX, MAXIMUM_TIMESTAMP_DIFFERENCE, Credential, stringify_credential_dicts
import sys
import secrets
data_dir = os.path.join(os.getcwd(), DATA_DIRECTORY)
BLOCKCHAIN:Blockchain
SMART_CONTRACT:Smart_Contract
def crea_blochcain():
    """
        Il seguente algoritmo crea la struttura della blockchain e istanzia uno smart contract, col quale le università possono comunicare
        Si presume che tutte le università siano a conoscenza della chiave pubblica dello smart contract, e che a sua volta lo smart contract sia a conoscenza
        di tutte le chiavi pubbliche delle università a cui è permesso manipolare la blockchain.
    """

    if not os.path.exists(BLOCKCHAIN_FOLDER):
        os.makedirs(BLOCKCHAIN_FOLDER)
    if not os.path.exists(os.path.join(BLOCKCHAIN_FOLDER, "blockchain.json")):
        BLOCKCHAIN = Blockchain()
        SMART_CONTRACT = Smart_Contract(BLOCKCHAIN, Parametric_Asymmetric_Scheme(), None)
        with open(os.path.join(BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
            data = {
                "blockchain": BLOCKCHAIN.save_on_json(),
                "smart_contract": SMART_CONTRACT.save_on_json()
            }
            json.dump(data, f, indent=4)
    else:
        with open(os.path.join(BLOCKCHAIN_FOLDER, "blockchain.json"), 'r') as f:
            blockchain_data = json.load(f)
        if "smart_contract" in blockchain_data:
            SMART_CONTRACT = Smart_Contract.load_from_json(blockchain_data["smart_contract"])
        else:
            raise ValueError("Il file blockchain.json non contiene lo smart contract.")
        if "blockchain" in blockchain_data:
            BLOCKCHAIN = Blockchain.load_from_json(blockchain_data["blockchain"])
        else:
            raise ValueError("Il file blockchain.json non contiene la blockchain.")
        SMART_CONTRACT._link_blockchain(BLOCKCHAIN) # Perdita del riferimento dopo lettura

def lettura_dati() -> tuple[dict, dict, dict, dict]:
    """
        L'algoritmo legge i dati e le configurazioni dai file JSON presenti nella cartella "data".
    """

    crea_blochcain()

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
    student.send(university, message, sign=True)
    #* 4 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di definire una password con la quale potrà autenticarsi successivamente
    #* Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_nonce_challenge = received_data["nonce"]
    received_timestamp = received_data["timestamp"]
    # Controlla che la differenza del timestamp non superi la costante MAXIMUM_TIMESTAMP_DIFFERENCE
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    uni_message = {
        "text": f"Benvenuto {received_data['name']} {received_data['surname']}, per favore fornisci una password per autenticarti in futuro, inoltre, ripeti il timestamp originale e l'attuale",
        "nonce": received_data["timestamp"],
        "timestamp": time.time()
    }
    university.send(student, Message(json.dumps(uni_message)), encrypt=False, sign=True)

    #* 5 Lo studente riceve il messaggio e procede a definire una password
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())
    if received_data['nonce'] != received_data['timestamp']:
        raise ValueError("Il timestamp del messaggio dell'università non corrisponde a quello originale, possibile replay attack.")
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    if len(args) > 4:
        password = args[4]
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
        "nonce": random_number,
        "text": "Password di immatricolazione"
    }

    student.send(university, Message(json.dumps(password_message)), sign=True)
    #* 6 L'università riceve la password e la salva nel proprio database, immatricolando lo studente
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    if received_data['nonce'] != received_nonce_challenge:
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

    #* La CA genera una coppia di chiavi per sé e per i certificati
    scheme = Parametric_Asymmetric_Scheme()
    ca.add_key(ca, scheme)

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

    scheme: Asymmetric_Scheme = Parametric_Asymmetric_Scheme()
    public_key = scheme.share_public_key()
    university.add_key(university, scheme)
    university.add_key(ca, ca._keys[ca._code].share_public_key()) # type: ignore 

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

    ca.send(university, certificate, authority=True)

    print(f"L'università {university.get_name()} è stata certificata con successo dalla CA {ca.get_code()}.")

def autenticazione(args:list[str]=[]):
    """
        Funzione per autenticare uno studente.
    """
    students = lettura_dati()[0]
    universities = lettura_dati()[1]

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
    student.send(university, message, sign=True)
    #* 2 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di inserire la password per autenticarsi
    #* Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
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
    if received_data['nonce'] != received_data['timestamp']:
        raise ValueError("Il timestamp del messaggio dell'università non corrisponde a quello originale, possibile replay attack.")

    student_scheme = Parametric_Symmetric_Scheme()
    password_message = {
        "password": student.get_password(university),
        "timestamp": time.time(),
        "nonce": random_number,
        "text": "Password di autenticazione",
        "scheme": student_scheme.save_on_json()
    }
    student.send(university, Message(json.dumps(password_message)), sign=True)
    student.add_key(university, student_scheme)
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
        "text": f"Autenticazione avvenuta con successo {student.get_name()} {student.get_surname()} ({student.get_code()})",
        "timestamp": time.time(),
    }
    uni_scheme = Parametric_Symmetric_Scheme.load_from_json(received_data.get("scheme"))
    university.add_key(student, uni_scheme)
    university.send(student, Message(json.dumps(auth_message)), encrypt=True, sign=True)
    print("Lo studente si è autenticato con successo, comunicazione cifrata stabilita.")

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

def emetti_credenziale(args:list[str]=[]):
    """
        Funzione per emettere una credenziale di uno studente in mobilità iscritto ad un'università ospitante.
    """
    students = lettura_dati()[0]
    universities = lettura_dati()[1]

    university_code = read_code("Inserisci il codice dell'università ospitante: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università ospitante non esiste.")
        university_code = read_code("Inserisci il codice dell'università ospitante: ")
    
    student_code = read_code("Inserisci il codice dello studente: ", args[1] if len(args) > 1 else None)
    while student_code not in students:
        print("Lo studente non esiste.")
        student_code = read_code("Inserisci il codice dello studente: ")

    autenticazione([university_code, student_code] + args[2:])  # Assicura che lo studente sia autenticato prima di emettere la credenziale
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
    hashing_algorithm = BLOCKCHAIN.get_hashing_algorithm()
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
    university.send(SMART_CONTRACT, request_message, sign=True)

    received_data = SMART_CONTRACT.get_last_message().get_content()
    received_data = json.loads(received_data)
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    
    if SMART_CONTRACT.is_blacklisted(university):
        raise ValueError("L'università è stata inserita nella blacklist dello smart contract, impossibile procedere con la certificazione della credenziale.")
    
    #* 4 Lo smart contract verifica la richiesta e costruisce il merkle_tree
    mt = MerkleTree(merkle_leafs, hashing_algorithm)
    credential_ID = SMART_CONTRACT.certificate_credential_MerkleTree(mt, university)


    #* 5 Lo smart contract risponde all'università con l'ID della credenziale
    response_message = {
        "timestamp": time.time(),
        "credential_ID": credential_ID,
        "text": "Credenziale certificata con successo nella blockchain"
    }
    response_message = Message(json.dumps(response_message))
    SMART_CONTRACT.send(university, response_message, sign=True)
    
    
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

    with open(os.path.join(BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
        data = {
            "blockchain": BLOCKCHAIN.save_on_json(),
            "smart_contract": SMART_CONTRACT.save_on_json()
        }
        json.dump(data, f, indent=4)
    
def divulga_credenziale(credenziale:Credential, args:list[str]=[]) -> Credential:
    print(" *** Divulgazione Selettiva della Credenziale *** ")
    lista_esami = {exam["name"]: exam for exam in credenziale["exams_results"]}
    lista_attivita = {activity["name"]: activity for activity in credenziale["activities_results"]}


    print("Esami disponibili: ", f" {', '.join(lista_esami.keys())}")
    print("Attività disponibili: ", f" {', '.join(lista_attivita.keys())}")

    action = input("Inserisci E per rimuovere un esame, oppure A per rimuovere una attività, o premi invio per continuare: ")
    while action:
        if action.lower() == "e":
            esame = input("Inserisci il nome dell'esame da rimuovere: ")
            if esame in lista_esami:
                del lista_esami[esame]
                print(f"Esame {esame} rimosso.")
            else:
                print(f"Esame {esame} non trovato.")
        elif action.lower() == "a":
            attivita = input("Inserisci il nome dell'attività da rimuovere: ")
            if attivita in lista_attivita:
                del lista_attivita[attivita]
                print(f"Attività {attivita} rimossa.")
            else:
                print(f"Attività {attivita} non trovata.")
        else:
            print("Azione non valida, riprova.")
        
        action = input("Inserisci E per rimuovere un esame, oppure A per rimuovere una attività, o premi invio per continuare: ")

    #* 1 Lo studente seleziona gli esami e le attività da rimuovere dalla credenziale
    credenziale["exams_results"] = list(lista_esami.values())
    credenziale["activities_results"] = list(lista_attivita.values())

    return credenziale

def presenta_credenziale(args:list[str]=[]):
    students = lettura_dati()[0]
    universities = lettura_dati()[1]

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

    autenticazione([university_code, student_code])  # Assicura che lo studente sia autenticato prima di validare la credenziale

    #* 1 Lo studente effettua la divulgazione selettiva della propria credenziale
    new_credential = divulga_credenziale(credential, args[2:]) if len(args) > 2 else divulga_credenziale(credential)

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
    received_credential_id = received_data["credential_id"]
    received_nonce = received_data["nonce"]
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    #* 3 L'università verifica la credenziale e poi controlla la certificazione sulla blockchain
    if not university.check_matching(student, credential):
        raise ValueError("La credenziale non è valida.")

    hashing_algorithm = BLOCKCHAIN.get_hashing_algorithm()
    merkle_leafs = [hashing_algorithm.hash(data) for data in stringify_credential_dicts(received_credential)]

    request_certification_validation = {
        "timestamp": time.time(),
        "text": "Richiesta di validazione della certificazione",
        "credential": merkle_leafs,
        "credential_ID": received_credential_id,
    }

    request_message = Message(json.dumps(request_certification_validation))
    university.send(SMART_CONTRACT, request_message, sign=True)


    received_message = SMART_CONTRACT.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    received_leafs = received_data["credential"]
    received_ID = received_data["credential_ID"]
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    if SMART_CONTRACT.is_blacklisted(university):
        raise ValueError("L'università è stata inserita nella blacklist dello smart contract, impossibile procedere con la validazione della credenziale.")

    validation_results = SMART_CONTRACT.validate_credential_MerkleTreeLeafs(received_leafs, received_ID)

    #* 4 Lo smart contract risponde all'università con i risultati della validazione
    response_message = {
        "timestamp": time.time(),
        "validation_results": validation_results,
        "credential_ID": received_ID,
        "text": "Risultati della validazione della credenziale"
    }
    SMART_CONTRACT.send(university, Message(json.dumps(response_message)), sign=True)

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
        university.set_credential_id

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

if __name__ == "__main__":

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
    else:
        print(f"Comando sconosciuto: {command}")