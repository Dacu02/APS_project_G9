import json
import os
import time
from actors import University
from actors.Student import Student
from algorithms.lettura_dati import lettura_dati
from algorithms.logout import logout
from algorithms.read_code import read_code
from algorithms.autenticazione import autenticazione
from blockchain import MerkleTree
from communication import Message
from constants import BLOCKCHAIN_FOLDER, DATA_DIRECTORY, MAXIMUM_TIMESTAMP_DIFFERENCE, STUDENTS_FOLDER, stringify_credential_dicts, EXTRACT_RANDOM_NUMBER


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
    initial_nonce = EXTRACT_RANDOM_NUMBER()
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

    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students_data = json.load(f)
    students_data[student_code] = student.save_on_json()
    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump(students_data, f, indent=4)