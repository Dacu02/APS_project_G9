import json
import os
from actors import CA, Student, University
from blockchain import Smart_Contract, Blockchain
from communication import Parametric_Asymmetric_Scheme
from constants import BLOCKCHAIN_FOLDER, DATA_DIRECTORY, STUDENTS_FOLDER, UNIVERSITIES_FOLDER, CAs_FOLDER


def carica_blockchain()-> tuple[Blockchain, Smart_Contract]:
    """
        Il seguente algoritmo carica la struttura della blockchain e istanzia uno smart contract, col quale le università possono comunicare
        Si presume che tutte le università siano a conoscenza della chiave pubblica dello smart contract, e che a sua volta lo smart contract sia a conoscenza
        di tutte le chiavi pubbliche delle università a cui è permesso manipolare la blockchain.
    """

    if not os.path.exists(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER)):
        os.makedirs(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER))
    if not os.path.exists(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json")):
        blockchain = Blockchain()
        smart_contract = Smart_Contract(blockchain, Parametric_Asymmetric_Scheme(), None)
        with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
            data = {
                "blockchain": blockchain.save_on_json(),
                "smart_contract": smart_contract.save_on_json()
            }
            json.dump(data, f, indent=4)
    else:
        with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'r') as f:
            blockchain_data = json.load(f)
            blockchain = Blockchain.load_from_json(blockchain_data["blockchain"])
            smart_contract = Smart_Contract.load_from_json(blockchain_data["smart_contract"])
        smart_contract._link_blockchain(blockchain) # Perdita del riferimento dopo lettura
    return blockchain, smart_contract



def lettura_dati() -> tuple[dict[str, Student], dict[str, University], dict[str, CA], dict[str, str], Blockchain, Smart_Contract]:
    """
        L'algoritmo legge i dati e le configurazioni dai file JSON presenti nella cartella "data".
    """
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)

    if not os.path.exists(os.path.join(DATA_DIRECTORY, "config.json")):
        with open(os.path.join(DATA_DIRECTORY, "config.json"), 'w') as f:
            configurazione = {}
            # Eventuale configurazioni da inizializzare
            json.dump(configurazione, f, indent=4)

    if not os.path.exists(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER)):
        os.makedirs(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER))
    if not os.path.exists(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json")):
        with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
            students = {}
            # Eventuale lista di studenti da inizializzare
            json.dump(students, f, indent=4)

    if not os.path.exists(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER)):
        os.makedirs(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER))
    if not os.path.exists(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json")):
        with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
            universities = {}
            json.dump(universities, f, indent=4)

    if not os.path.exists(os.path.join(DATA_DIRECTORY, CAs_FOLDER)):
        os.makedirs(os.path.join(DATA_DIRECTORY, CAs_FOLDER))
    if not os.path.exists(os.path.join(DATA_DIRECTORY, CAs_FOLDER, "CAs.json")):
        with open(os.path.join(DATA_DIRECTORY, CAs_FOLDER, "CAs.json"), 'w') as f:
            CAs = {}
            json.dump(CAs, f, indent=4)

    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'r') as f:
        students = json.load(f)
    with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'r') as f:
        universities = json.load(f)
        private_uni_file = os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "uni_.json")
        if os.path.exists(private_uni_file):
            with open(private_uni_file, 'r') as f_priv:
                private_universities = json.load(f_priv)
                universities.update(private_universities)
    with open(os.path.join(DATA_DIRECTORY, CAs_FOLDER, "CAs.json"), 'r') as f:
        CAs = json.load(f)
    with open(os.path.join(DATA_DIRECTORY, "config.json"), 'r') as f:
        configurazione = json.load(f)

    for student_name, student_data in students.items():
        students[student_name] = Student.load_from_json(student_data)

    for university_name, university_data in universities.items():
        universities[university_name] = University.load_from_json(university_data)
    
    for ca_name, ca_data in CAs.items():
        CAs[ca_name] = CA.load_from_json(ca_data)

    return students, universities, CAs, configurazione, *carica_blockchain()
