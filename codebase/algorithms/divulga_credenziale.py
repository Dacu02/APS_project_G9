from constants import Credential


def divulga_credenziale(credenziale:Credential, args:list[str]=[]) -> Credential:
    print(" *** Divulgazione Selettiva della Credenziale *** ")
    lista_esami = {exam["name"]: exam for exam in credenziale["exams_results"]}
    lista_attivita = {activity["name"]: activity for activity in credenziale["activities_results"]}


    print("Esami disponibili: ", f" {', '.join(lista_esami.keys())}")
    print("Attività disponibili: ", f" {', '.join(lista_attivita.keys())}")
    i = 0
    if len(args) > i:
        action = args[i]
        i+=1
    else:
        action = input("Inserisci E per rimuovere un esame, oppure A per rimuovere una attività, o premi invio per continuare: ")
    while action:
        if action.lower() == "e":
            if len(args) > i:
                esame = args[i]
                i+=1
            else:
                esame = input("Inserisci il nome dell'esame da rimuovere: ")
            if esame in lista_esami:
                del lista_esami[esame]
                print(f"Esame {esame} rimosso.")
            else:
                print(f"Esame {esame} non trovato.")
        elif action.lower() == "a":
            if len(args) > i:
                attivita = args[i]
                i+=1
            attivita = input("Inserisci il nome dell'attività da rimuovere: ")
            if attivita in lista_attivita:
                del lista_attivita[attivita]
                print(f"Attività {attivita} rimossa.")
            else:
                print(f"Attività {attivita} non trovata.")
        else:
            print("Azione non valida, riprova.")
        if len(args) > i:
            action = args[i]
            i+=1
        else:
            action = input("Inserisci E per rimuovere un esame, oppure A per rimuovere una attività, o premi invio per continuare: ")

    #* Lo studente seleziona gli esami e le attività da rimuovere dalla credenziale

    credenziale["exams_results"] = list(lista_esami.values())
    credenziale["activities_results"] = list(lista_attivita.values())
    
    return credenziale
