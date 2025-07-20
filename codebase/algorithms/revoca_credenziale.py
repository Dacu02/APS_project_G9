
import json
import os
import time
from actors import University
from actors.Student import Student
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from communication import Message
from constants import BLOCKCHAIN_FOLDER, DATA_DIRECTORY, MAXIMUM_TIMESTAMP_DIFFERENCE


def revoca_credenziale(args:list[str]=[]):
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

    # Recupera l'ID della credenziale da revocare
    credential_ID = university.get_credential_id(student)
    if not credential_ID:
        raise ValueError("Credenziale non trovata.")


    # L'università invia la richiesta di revoca allo smart contract
    revoke_message = {
        "timestamp": time.time(),
        "credential_ID": credential_ID,
        "text": "Richiesta di revoca della credenziale"
    }
    message = Message(json.dumps(revoke_message))
    university.add_key(smart_contract, smart_contract.get_public_key())
    university.send(smart_contract, message, encrypt=False, sign=True)

    # Lo smart contract riceve la richiesta e revoca la credenziale
    received_message = smart_contract.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_credential_id = received_data["credential_ID"]
    received_timestamp = received_data["timestamp"]
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    if smart_contract.is_blacklisted(university):
        raise ValueError("L'università è stata inserita nella blacklist dello smart contract, impossibile procedere con la revoca.")
    try:
        smart_contract.revoke_credential(received_credential_id, university)
        revocation_result = True
    except ValueError as e:
        print(f"Errore nella revoca della credenziale: {e}")
        revocation_result = False

    # Lo smart contract risponde all'università con l'esito della revoca
    response_message = {
        "timestamp": time.time(),
        "credential_ID": received_credential_id,
        "revocation_result": revocation_result
    }
    smart_contract.send(university, Message(json.dumps(response_message)), sign=True)

    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())

    with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
        data = {
            "blockchain": blockchain.save_on_json(),
            "smart_contract": smart_contract.save_on_json()
        }
        json.dump(data, f, indent=4)

