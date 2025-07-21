from attacks import studente_malevolo, violazione_CA, violazione_ospitante, intercettatore_ospitante_studente, attacco_credenziale_nota, divulgazione_informazioni_superflue, violazione_origine
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
    elif nome == "divulgazione_informazioni_superflue":
        divulgazione_informazioni_superflue()
    elif nome == "violazione_origine":
        violazione_origine()
    else:
        exit()
except Exception as e:
    print(f"ERR: {e}")