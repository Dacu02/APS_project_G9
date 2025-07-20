from attacks import studente_malevolo, violazione_CA, violazione_universita, intercettatore_ospitante_studente
intercettatore_ospitante_studente()
nome = input("Inserisci il nome dell'attacco da simulare: ")
try:
    if nome == "studente_malevolo":
        studente_malevolo()
    elif nome == "violazione_CA":
        violazione_CA()
    elif nome == "violazione_universita":
        violazione_universita()
    elif nome == "intercettatore_ospitante_studente":
        intercettatore_ospitante_studente()
    else:
        exit()
except Exception as e:
    print(f"ERR: {e}")