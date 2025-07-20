

import json
from pkgutil import read_code
import secrets
import time
from actors import CA, University
from actors.Student import Student
from algorithms.lettura_dati import lettura_dati
from algorithms.logout import logout
from algorithms.read_code import read_code
from algorithms.autenticazione import autenticazione
from communication import Message
from constants import MAXIMUM_TIMESTAMP_DIFFERENCE, RANDOM_NUMBER_MAX, Activity, StudyPlan


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
