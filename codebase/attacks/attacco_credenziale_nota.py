import json
import os
import secrets
import time
from actors import University
from actors.Student import Student
from algorithms import *
from blockchain import MerkleTree
from communication import Message
from constants import BLOCKCHAIN_FOLDER, DATA_DIRECTORY, MAXIMUM_TIMESTAMP_DIFFERENCE, RANDOM_NUMBER_MAX, STUDENTS_FOLDER, ExamResult, _registra_attivita, _registra_esame, stringify_credential_dicts
from attacks import Attacker

def _emetti_credenziale(args:list[str]=[]):
    """
        Funzione per emettere una credenziale di uno studente in mobilità iscritto ad un'università ospitante.
        VIOLAZIONE: L'attaccante può intercettare i messaggi tra lo studente e l'università ospitante
    """
    ATTACKER = Attacker("Attaccante Credenziale Nota")
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

    print("L'attaccante potrebbe conoscere la credenziale, tuttavia è ignaro degli altri campi, in particolare del nonce che gli è necessario per poterla utilizzare. Inoltre, siccome lo schema di cifratura è simmetrico, e non ne conosce la chiave, non può forgiare nuovi messaggi.")
        
    edited_credential = credential
    edited_credential["exams_results"] = []
    edited_credential["activities_results"] = [] 

    credential_message = Message(json.dumps(credential_message))
    # university.send(student, credential_message, sign=True) # ! INTERCETTATO E ALTERATO
    
    ATTACKER.intercept_message(student, university, credential_message)  # L'attaccante intercetta il messaggio della credenziale
    new_credential_message = {
        "timestamp": time.time(),
        "credential": edited_credential,
        "credential_ID": 1234, # L'attaccante modifica l'ID della credenziale non conoscendone l'originale
        "nonce": secrets.randbelow(RANDOM_NUMBER_MAX),  # L'attaccante tenta di indovinare il nonce
    }
    new_credential_message = Message(json.dumps(new_credential_message))
    student._receive(university, new_credential_message, decrypt=True, verify=True)
    #! A causa di assenza di cifratura e firma, lo stdente non può verificare l'autenticità del messaggio ricevuto
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

    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)
    students_data[student_code] = student.save_on_json()
    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)

def attacco_credenziale_nota():
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

    
    _registra_esame(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Analisi",
        "grade": 29,
        "lodging": False,
        "date": "2023-07-15",
        "prof": "Prof. Neri",
        "study_plan_name": "Matematica",
        "cfus": 4
    })

    _registra_attivita(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Ricerca",
        "cfus": 3,
        "start_date": "2025-06-06",
        "end_date": "2025-07-06",
        "prof": "Prof. Rossi"
    })

    _emetti_credenziale([COD_UNI_EXT, COD_STUDENTE, "TEST_PW_EXT"])
    