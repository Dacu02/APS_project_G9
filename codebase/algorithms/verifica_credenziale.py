
import json
import time
from actors import University
from actors.Student import Student
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from communication import Message
from constants import MAXIMUM_TIMESTAMP_DIFFERENCE

def verifica_credenziale(args:list[str]=[]):
    students, universities, _, _, _, smart_contract = lettura_dati()

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

    # Recupera l'ID della credenziale dello studente
    credential_ID = university.get_credential_id(student)
    if not credential_ID:
        raise ValueError("Credenziale non trovata per lo studente.")

    # L'università invia la richiesta di verifica allo smart contract
    verify_message = {
        "timestamp": time.time(),
        "credential_ID": credential_ID,
        "text": "Richiesta di verifica della validità della credenziale"
    }
    message = Message(json.dumps(verify_message))
    university.add_key(smart_contract, smart_contract.get_public_key())
    university.send(smart_contract, message, encrypt=False, sign=True)

    # Lo smart contract riceve la richiesta e verifica la validità della credenziale
    received_message = smart_contract.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_credential_id = received_data["credential_ID"]
    received_timestamp = received_data["timestamp"]
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    if smart_contract.is_blacklisted(university):
        raise ValueError("L'università è stata inserita nella blacklist dello smart contract, impossibile procedere con la verifica.")

    is_valid = smart_contract.validate_credential_ID(received_credential_id)

    # Lo smart contract risponde all'università con l'esito della verifica
    response_message = {
        "timestamp": time.time(),
        "credential_ID": received_credential_id,
        "is_valid": is_valid
    }
    smart_contract.send(university, Message(json.dumps(response_message)), sign=True)


    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    if not received_data.get("credential_ID") == credential_ID:
        raise ValueError("L'ID della credenziale ricevuto non corrisponde a quello inviato.")
    if abs(time.time() - received_data['timestamp']) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")


    received_is_valid = received_data["is_valid"]
    if not received_is_valid:
        university.set_credential(student, None, None)
    print(f"Credenziale {'valida' if is_valid else 'non valida'}.")
