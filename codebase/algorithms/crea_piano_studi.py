

from actors import University
from algorithms.lettura_dati import lettura_dati
from algorithms.read_code import read_code


def crea_piano_studi(args:list[str]=[]):
    universities:dict[str, University] = lettura_dati()[1]
    university_code = read_code("Inserisci il codice dell'università: ", args[0] if len(args) > 0 else None)
    while university_code not in universities:
        print("L'università non esiste.")
        university_code = read_code("Inserisci il codice dell'università: ")
    
    if len(args) > 1:
        study_plan_name = args[1]
    else:
        study_plan_name = input("Inserisci il nome del piano di studi: ")

    while study_plan_name in universities[university_code].get_study_plans():
        print("Il piano di studi esiste già.")
        study_plan_name = input("Inserisci il nome del piano di studi: ")

    i = 2
    study_plan = []
    while True:
        if len(args) > i:
            course_name = args[i] # Esce in automatico se args[i] = ""
            i+=1
        else:
            course_name = input("Inserisci il nome del corso (o premi invio per terminare): ")
        if not course_name:
            break

        if len(args) > i:
            course_credit = args[i]
            i+=1
        else:
            course_credit = input("Inserisci il numero di crediti del corso: ")
        while not course_credit.isdigit():
            print("Il numero di crediti deve essere un numero.")
            course_credit = input("Inserisci il numero di crediti del corso: ")

        study_plan.append({"name": course_name, "cfus": int(course_credit)})
        
    if not study_plan:
        print("Piano di studi vuoto, non verrà creato.")
        return
    
    universities[university_code].add_study_plan(study_plan_name, study_plan)