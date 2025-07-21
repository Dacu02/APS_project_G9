import json
import os
import sys
import time

from algorithms import *
from constants import BLOCKCHAIN_FOLDER, DATA_DIRECTORY, MAXIMUM_TIMESTAMP_DIFFERENCE, _registra_attivita, _registra_esame
from communication import Message
from actors import *

def vota_estromissione_universita(voter_uni_code:str, voted_uni_code:str, cod_CA:str):
    _, universities, CAs, _, blockchain, smart_contract = lettura_dati()
    voter_university = universities[voter_uni_code]
    voted_university = universities[voted_uni_code]
    ca = CAs[cod_CA]
    
    # Si presume che l'università conosca giò la chiave dello smart contract
    voter_university.add_key(smart_contract, smart_contract.get_public_key())

    estromission_message = {
        "timestamp": time.time(),
        "text": "Voto l'estromissione di una universita\' dal sistema",
        "voted_university": voted_uni_code
    }
    message = Message(json.dumps(estromission_message))
    voter_university.send(smart_contract, message, encrypt=True, sign=True)


    received_message = smart_contract.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data["timestamp"]
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    if smart_contract.is_blacklisted(voter_university):
        raise ValueError("L'università è stata inserita nella blacklist dello smart contract, impossibile procedere con la verifica.")

    smart_contract.vote_blacklist(smart_contract._keys[voter_university.get_code()], universities[voted_uni_code]) # type: ignore
    
    with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
        data = {
            "blockchain": blockchain.save_on_json(),
            "smart_contract": smart_contract.save_on_json()
        }
        json.dump(data, f, indent=4)



def violazione_origine():
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


    UNIS = [UNI1, UNI2, UNI3] = "313", "626", "939"
    for uni in UNIS:
        crea_universita([uni, f"Università {uni}"])
        certifica_universita([_CA, uni])


    vota_estromissione_universita(UNI1, COD_UNI_INT, _CA)
    vota_estromissione_universita(UNI3, COD_UNI_INT, _CA)
    
    emetti_credenziale([COD_UNI_EXT, COD_STUDENTE, "TEST_PW_EXT"])
    # ! Può accadere che l'università interna venga violata o che venga rimossa dalla blockchain da altre università

    presenta_credenziale([COD_STUDENTE, COD_UNI_INT, 'TEST_PW', 'E', "Fisica", ""])
    # revoca_credenziale([COD_STUDENTE, COD_UNI_EXT])
    verifica_credenziale([COD_STUDENTE, COD_UNI_INT])