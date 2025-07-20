import os
import json
import time
import secrets

from algorithms.lettura_dati import lettura_dati
from actors import CA, Student, University
from communication import Certificate, Message
from constants import DATA_DIRECTORY, MAXIMUM_TIMESTAMP_DIFFERENCE, RANDOM_NUMBER_MAX, STUDENTS_FOLDER


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
    students, universities, CAs = lettura_dati()[0:3] # type: ignore
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
    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump({code: s.save_on_json() for code, s in students.items()}, f, indent=4)

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
