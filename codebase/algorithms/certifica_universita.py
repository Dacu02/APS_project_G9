import json
import os
from actors import CA, University
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from communication import Asymmetric_Scheme, Parametric_Asymmetric_Scheme
from constants import BLOCKCHAIN_FOLDER, DATA_DIRECTORY, UNIVERSITIES_FOLDER, CAs_FOLDER


def certifica_universita(args:list[str]=[]):
    """
        Funzione per certificare un'università, richiede il nome della CA e dell'università.
        L'università genera una coppia di chiavi, e chiede alla CA di pubblicare la propria chiave pubblica attraverso un certificato.
    """
    _, universities, CAs, _, _, smart_contract = lettura_dati()
    if len(args) > 0:
        ca_name = args[0]
    else:
        ca_name = input("Inserisci il nome della CA: ")
    while ca_name not in CAs:
        print("La CA non esiste.")
        ca_name = input("Inserisci il nome della CA: ")

    university_code = read_code("Inserisci il codice dell'università: ", args[1] if len(args) > 1 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    ca:CA = CAs[ca_name]
    university:University = universities[university_code]

    #* 1 L'università genera una coppia di chiavi

    scheme: Asymmetric_Scheme = Parametric_Asymmetric_Scheme()
    public_key = scheme.share_public_key()
    university.add_key(university, scheme)
    university.add_key(ca, ca.get_public_key()) 

    # Si immagina che l'università conosca già la CA sulla quale vuole certificare
    # la chiave pubblica e che comunichi attraverso altri mezzi alternativi sicuri
    # Discorso analogo per la registrazione della chiave pubblica all'interno dello smart contract


    #* 2 L'università chiede alla CA di certificare la propria chiave pubblica
    cert = ca.register_user_public_key(university, public_key)
    ca.add_key(university, public_key)
    
    if cert is None:
        raise ValueError(f"La CA {ca_name} non ha potuto certificare l'università {university_code}.")
    
    #* 3 La CA restituisce il certificato all'università
    certificate = ca.get_user_certificate(university)
    if certificate is None:
        raise ValueError(f"La CA {ca_name} non ha emesso correttamente il certificato per l'università {university_code}.")

    ca.send(university, certificate, encrypt=False)
    smart_contract.register_university(university, public_key)
    print(f"L'università {university.get_name()} è stata certificata con successo dalla CA {ca.get_code()}.")

    # Salva le chiavi aggiornate della CA e dell'università nei rispettivi file JSON
    with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump({code: uni.save_on_json() for code, uni in universities.items()}, f, indent=4)
    with open(os.path.join(DATA_DIRECTORY, CAs_FOLDER, "CAs.json"), 'w') as f:
        json.dump({name: ca_obj.save_on_json() for name, ca_obj in CAs.items()}, f, indent=4)

    with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'r') as f:
        data = json.load(f)
    data["smart_contract"] = smart_contract.save_on_json()
    with open(os.path.join(DATA_DIRECTORY, BLOCKCHAIN_FOLDER, "blockchain.json"), 'w') as f:
        json.dump(data, f, indent=4)
