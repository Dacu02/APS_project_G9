from algorithms import *
from constants import _registra_attivita, _registra_esame

def violazione_CA():
    COD_UNI_INT = "001"
    COD_UNI_EXT = "002"
    COD_STUDENTE = "010"

    CA_VIOLATO = "CA_V"

    pulizia()
    crea_CA([CA_VIOLATO])

    crea_universita([COD_UNI_INT, "UniInt"])
    certifica_universita([CA_VIOLATO, COD_UNI_INT])
    crea_piano_studi([COD_UNI_INT, "Informatica", "Programmazione", "6", "Sistemi Operativi", "6", "Analisi", "3", ""])
    crea_attivita([COD_UNI_INT, "Ricerca", "3"])

    crea_universita([COD_UNI_EXT, "UniExt"])
    certifica_universita([CA_VIOLATO, COD_UNI_EXT])
    crea_piano_studi([COD_UNI_EXT, "Matematica", "Fisica", "4", "Analisi", "4", ""])
    crea_attivita([COD_UNI_EXT, "Ricerca", "3"])
    crea_studente([COD_STUDENTE, "Mario", "Rossi"])


    immatricola([COD_STUDENTE, COD_UNI_INT, CA_VIOLATO, "Informatica", "TEST_PW"])

    print("Lo studente è ora immatricolato presso una università falsa, oppure un attaccante che è ora in grado di decifrare i messaggi che invierà all'università, siccome potrebbe avere calcoato una coppia di chiavi e inviato la pubblica.")
    input("Il seguente progetto non implementa una contromisura per il seguente attacco, tuttavia una possibile soluzione è già descritta all'interno della documentazione")
    exit(1)

    _registra_esame(COD_UNI_INT, COD_STUDENTE, {
        "name":"Programmazione",
        "grade":28,
        "lodging":False,
        "date":"2023-05-15",
        "prof":"Prof. Rossi",
        "study_plan_name":"Informatica",
        "cfus":6
    })
    
    _registra_esame(COD_UNI_INT, COD_STUDENTE, {
        "name": "Sistemi Operativi",
        "grade": 30,
        "lodging": True,
        "date": "2023-06-10",
        "prof": "Prof. Bianchi",
        "study_plan_name": "Informatica",
        "cfus": 6
    })

    domanda_mobilita([COD_UNI_INT, COD_UNI_EXT, COD_STUDENTE, "TEST_PW", "Analisi", "3", "", "Ricerca", "3", "", "R_INT", CA_VIOLATO, "R_EXT"])

    immatricola([COD_STUDENTE, COD_UNI_EXT, CA_VIOLATO, "TEST_PW_EXT"])

    _registra_esame(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Fisica",
        "grade": 27,
        "lodging": False,
        "date": "2023-07-01",
        "prof": "Prof.ssa Verdi",
        "study_plan_name": "Matematica",
        "cfus": 4
    })

    _registra_esame(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Analisi",
        "grade": 29,
        "lodging": False,
        "date": "2023-07-15",
        "prof": "Prof. Neri",
        "study_plan_name": "Matematica",
        "cfus": 4
    })

    _registra_attivita(COD_UNI_EXT, COD_STUDENTE, {
        "name": "Ricerca",
        "cfus": 3,
        "start_date": "2025-06-06",
        "end_date": "2025-07-06",
        "prof": "Prof. Rossi"
    })

    emetti_credenziale([COD_UNI_EXT, COD_STUDENTE, "TEST_PW_EXT"])

    presenta_credenziale([COD_STUDENTE, COD_UNI_INT, 'TEST_PW', 'E', "Fisica", ""])
    revoca_credenziale([COD_STUDENTE, COD_UNI_EXT])
    verifica_credenziale([COD_STUDENTE, COD_UNI_INT])