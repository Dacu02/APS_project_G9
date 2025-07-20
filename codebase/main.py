
import sys
from algorithms import *
from algorithms import logout, presenta_credenziale, revoca_credenziale
from constants import _registra_attivita, _registra_esame


# FUNZIONI PER TESTING

COD_UNI_INT = "001"
COD_UNI_EXT = "002"
COD_STUDENTE = "010"
_CA = "CA1"
pulizia()
crea_CA([_CA])

crea_universita([COD_UNI_INT, "UniInt"])
certifica_universita([_CA, COD_UNI_INT])
crea_piano_studi([COD_UNI_INT, "Informatica", "Programmazione", "6", "Sistemi Operativi", "6", "Analisi", "3", ""])
crea_attivita([COD_UNI_INT, "Ricerca", "3"])

crea_universita([COD_UNI_EXT, "UniExt"])
certifica_universita([_CA, COD_UNI_EXT])
crea_piano_studi([COD_UNI_EXT, "Matematica", "Fisica", "4", "Analisi", "4", ""])
crea_attivita([COD_UNI_EXT, "Ricerca", "3"])
crea_studente([COD_STUDENTE, "Mario", "Rossi"])


immatricola([COD_STUDENTE, COD_UNI_INT, _CA, "Informatica", "TEST_PW"])

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

domanda_mobilita([COD_UNI_INT, COD_UNI_EXT, COD_STUDENTE, "TEST_PW", "Analisi", "3", "", "Ricerca", "3", "", "R_INT", _CA, "R_EXT"])

immatricola([COD_STUDENTE, COD_UNI_EXT, _CA, "TEST_PW_EXT"])

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
exit(0)

if len(sys.argv) < 2:
    print("Inserisci il nome di un algoritmo")
    command = input("Comando: ")
else:
    command = sys.argv[1]

if command == "pulizia":
    pulizia()
elif command == "crea_studente":
    crea_studente(list(sys.argv[2:]))
elif command == "crea_universita":
    crea_universita(list(sys.argv[2:]))
elif command == "crea_piano_studi":
    crea_piano_studi(list(sys.argv[2:]))
elif command == "crea_attivita":
    crea_attivita(list(sys.argv[2:]))
elif command == "crea_CA":
    crea_CA(list(sys.argv[2:]))
elif command == "immatricola":
    immatricola(list(sys.argv[2:]))
elif command == "certifica_universita":
    certifica_universita(list(sys.argv[2:]))
elif command == "emetti_credenziale":
    emetti_credenziale(list(sys.argv[2:]))
elif command == "presenta_credenziale":
    presenta_credenziale(list(sys.argv[2:]))
elif command == "domanda_mobilita":
    domanda_mobilita(list(sys.argv[2:]))
elif command == "logout":
    logout(list(sys.argv[2:]))
elif command == "revoca_credenziale":
    revoca_credenziale(list(sys.argv[2:]))
elif command == "verifica_credenziale":
    verifica_credenziale(list(sys.argv[2:]))
else:
    print(f"Comando sconosciuto: {command}")

