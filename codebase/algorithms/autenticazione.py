
import json
import os
import secrets
import time
from actors import Student, University
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from communication import Message, Parametric_Symmetric_Scheme
from constants import DATA_DIRECTORY, MAXIMUM_TIMESTAMP_DIFFERENCE, RANDOM_NUMBER_MAX, STUDENTS_FOLDER, UNIVERSITIES_FOLDER


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
    RANDOM_NUMBER0 = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 999999 non basato su timestamp
    RANDOM_NUMBER1 = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 999999 non basato su timestamp
    #* 1 Lo studente invia un messaggio all'università con il proprio nome, cognome, codice, timestamp e un numero casuale
    message_data = {
        "name": student.get_name(),
        "surname": student.get_surname(),
        "code": student.get_code(),
        "timestamp": student_initial_timestamp,
        "text": "Autenticazione",
        "nonce0": RANDOM_NUMBER0,
        "nonce1": RANDOM_NUMBER1
    }

    message = Message(json.dumps(message_data))
    student.send(university, message, sign=False)
    #* 2 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di inserire la password per autenticarsi
    ## !OLD Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    #* Per evitare replay attack, l'università chiede allo studente di fornire l'altro nonce casuale
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    first_received_timestamp = received_data['timestamp']
    if abs(time.time() - first_received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    NONCE_CHALLENGE_0 = received_data["nonce0"]
    NONCE_CHALLENGE_1 = received_data["nonce1"]
    uni_message = {
        "text": f"Benvenuto {received_data['name']} {received_data['surname']}, per favore fornisci una password per autenticarti, inoltre, forniscimi il nonce1",
        "nonce": received_data["timestamp"],
        "timestamp": time.time(),
        "nonce": NONCE_CHALLENGE_0,
    }
    university.send(student, Message(json.dumps(uni_message)), encrypt=False, sign=True)

    #* 3 Lo studente riceve il messaggio e procede a inserire la password
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    if received_data['nonce'] != RANDOM_NUMBER0:
        raise ValueError("Il nonce del messaggio dell'università non corrisponde a quello originale, possibile replay attack.")


    student_scheme = Parametric_Symmetric_Scheme()
    password_message = {
        "password": student.get_password(university),
        "timestamp": time.time(),
        "nonce": RANDOM_NUMBER1,
        "text": "Password",
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
    if received_data['nonce'] != NONCE_CHALLENGE_1:
        raise ValueError("Il numero casuale del messaggio dello studente non corrisponde a quello originale, possibile replay attack.")
    check = university.check_password(student, received_data["password"])
    if not check:
        raise ValueError("Password errata, impossibile autenticare lo studente.")
    print(f"Autenticazione dello studente {student.get_name()} {student.get_surname()} ({student.get_code()}) avvenuta con successo.")
    
    #* 5 L'università risponde allo studente con un messaggio di autenticazione avvenuta con successo con attraverso la nuova chiave
    auth_message = {
        "text": f"Autenticazione avvenuta con successo {student.get_name()} {student.get_surname()} ({student.get_code()}). Inviami uno schema simmetrico casuale a partire dal secondo nonce inviato",
        "timestamp": time.time(),
    }
    
    # university.add_key(student, uni_scheme)
    university.send(student, Message(json.dumps(auth_message)), encrypt=False, sign=True)
    print("Lo studente si è autenticato con successo, comunicazione cifrata da stabilire.")


    # Comunicazione delle componenti della chiave TCP style
    sender_k = RANDOM_NUMBER1
    receiver_k = NONCE_CHALLENGE_1
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

    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)
    with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'r') as f:
        universities_data = json.load(f)    

    students_data[student_code] = student.save_on_json()
    universities_data[university_code] = university.save_on_json()

    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)
    with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump(universities_data, f, indent=4)
