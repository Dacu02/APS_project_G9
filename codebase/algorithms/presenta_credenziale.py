
import json
import secrets
import time
from actors import University
from actors.Student import Student
from algorithms.lettura_dati import lettura_dati
from algorithms.logout import logout
from algorithms.read_code import read_code
from algorithms.autenticazione import autenticazione
from algorithms.divulga_credenziale import divulga_credenziale
from constants import MAXIMUM_TIMESTAMP_DIFFERENCE, RANDOM_NUMBER_MAX, stringify_credential_dicts
from communication import Message


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
    if validation_results:
        print("Credenziale presentata con successo.")
    else:
        raise ValueError("La credenziale non è valida o non è stata accettata dall'università.")
