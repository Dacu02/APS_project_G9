import json
import os
from actors import University
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from constants import BLOCKCHAIN_HASH_ALGORITHM, DATA_DIRECTORY, UNIVERSITIES_FOLDER


def crea_universita(args:list[str]=[]):
    universities:dict[str, University] = lettura_dati()[1]
    code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while code in universities:
        print("L'università esiste già.")
        code = read_code("Inserisci il codice dell'università: ")
    
    if len(args) > 1:
        name = args[1]
    else:
        name = input("Inserisci il nome dell'università: ")
    
    print("Università creata con successo.")
    university = University(name, code, BLOCKCHAIN_HASH_ALGORITHM())
    universities[code] = university
    with open(os.path.join(DATA_DIRECTORY, UNIVERSITIES_FOLDER, "universities.json"), 'w') as f:
        json.dump({code: university.save_on_json() for code, university in universities.items()}, f, indent=4)
