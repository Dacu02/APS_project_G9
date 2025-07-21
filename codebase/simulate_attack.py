from attacks import studente_malevolo, violazione_CA, violazione_ospitante, intercettatore_ospitante_studente, attacco_credenziale_nota
intercettatore_ospitante_studente()
nome = input("Inserisci il nome dell'attacco da simulare: ")
try:
    if nome == "studente_malevolo":
        studente_malevolo()
    elif nome == "violazione_CA":
        violazione_CA()
    elif nome == "violazione_ospitante":
        violazione_ospitante()
    elif nome == "intercettatore_ospitante_studente":
        intercettatore_ospitante_studente()
    elif nome == "attacco_credenziale_nota":
        attacco_credenziale_nota()
    else:
        exit()
except Exception as e:
    print(f"ERR: {e}")