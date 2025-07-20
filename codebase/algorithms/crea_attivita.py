
from actors import University
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code
from constants import Activity


def crea_attivita(args:list[str]=[]):
    universities:dict[str, University] = lettura_dati()[1]
    university_code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")

    if len(args) > 1:
        activity_name = args[1]
    else:
        activity_name = input("Inserisci il nome dell'attività: ")

    if len(args) > 2:
        activity_credit = args[2]
    else:
        activity_credit = input("Inserisci il numero di crediti dell'attività: ")
    while not activity_credit.isdigit():
        print("Il numero di crediti deve essere un numero.")
        activity_credit = input("Inserisci il numero di crediti dell'attività: ")

    activity:Activity = {"name": activity_name, "cfus": int(activity_credit)}

    universities[university_code].add_activity(activity)