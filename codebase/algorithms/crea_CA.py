import json
import os
from actors import CA
from algorithms.lettura_dati import lettura_dati
from communication import Parametric_Asymmetric_Scheme
from constants import DATA_DIRECTORY, CAs_FOLDER


def crea_CA(args:list[str]=[]):
    CAs = lettura_dati()[2]
    if len(args) > 0:
        name = args[0]
    else:
        name = input("Inserisci il nome della CA: ")
    while name in CAs:
        print("La CA esiste già.")
        name = input("Inserisci il nome della CA: ")
    
    print("CA creata con successo.")
    ca = CA(name)
    CAs[name] = ca

    #* La CA genera una coppia di chiavi per sé e per i certificati
    scheme = Parametric_Asymmetric_Scheme()
    ca.add_key(ca, scheme)

    with open(os.path.join(DATA_DIRECTORY, CAs_FOLDER, "CAs.json"), 'w') as f:
        json.dump({name: ca.save_on_json() for name, ca in CAs.items()}, f, indent=4)