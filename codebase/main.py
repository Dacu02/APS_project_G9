
import sys
import time
from pympler import asizeof
from algorithms import *
from algorithms import logout, presenta_credenziale, revoca_credenziale
from constants import _registra_attivita, _registra_esame

char_input = input("Inserisci H per una esecuzione guidata, o A per una esecuzione automatica con valutazione del tempo di esecuzione, oppure C per eseguire un comando specifico: ")

if char_input == "H" or char_input == "A":
    if char_input == "H":
        print("Esecuzione guidata")
    else:
        print("Esecuzione automatica con valutazione del tempo di esecuzione")

    COD_UNI_INT = "001"
    COD_UNI_EXT = "002"
    COD_STUDENTE = "010"
    _CA = "CA1"

    #################### INIZIO PULIZIA #######################
    pulizia()
    if char_input == "H":
        x = input("Pulizia del dati salvati precedentemente...")
    else:
        START_TIME = time.time()
    ##########################################################


    ################## CREAZIONE CA ###################
    crea_CA([_CA])
    if char_input == "H":
        x = input("CA creata...")
    ###################################################


    ################## CREAZIONE UNIVERSITA' INTERNA ###################
    crea_universita([COD_UNI_INT, "UniInt"])
    if char_input == "H":
        x = input("Università interna creata...")
    #####################################################################


    ################## CERTIFICAZIONE UNIVERSITà INTERNA #################
    if char_input == "A":
        CERTIFICA_INT_START_TIME = time.time()

    certifica_universita([_CA, COD_UNI_INT])

    if char_input == "H":
        x = input("Università interna certificata...")
    else:
        CERTIFICA_INT_END_TIME = time.time() - CERTIFICA_INT_START_TIME # type: ignore
    #####################################################################


    ################## CREAZIONE PIANO DI STUDI INTERNO E ATTIVITA' ###################
    crea_piano_studi([COD_UNI_INT, "Informatica", "Programmazione", "6", "Sistemi Operativi", "6", "Analisi", "3", ""])
    if char_input == "H":
        x = input("Piano di studi creato...")

    crea_attivita([COD_UNI_INT, "Ricerca", "3"])
    if char_input == "H":
        x = input("Attività creata...")

    crea_universita([COD_UNI_EXT, "UniExt"])
    if char_input == "H":
        x = input("Università esterna creata...")
    ###################################################################################
    

    ################## CERTIFICAZIONE UNIVERSITà ESTERNA #################
    if char_input == "A":
        CERTIFICA_EXT_START_TIME = time.time()
    certifica_universita([_CA, COD_UNI_EXT])
    if char_input == "H":
        x = input("Università esterna certificata...")
    else:
        CERTIFICA_EXT_END_TIME = time.time() - CERTIFICA_EXT_START_TIME # type: ignore
    #####################################################################


    ################## CREAZIONE PIANO DI STUDI ESTERNO E ATTIVITA' ###################
    crea_piano_studi([COD_UNI_EXT, "Matematica", "Fisica", "4", "Analisi", "4", ""])
    if char_input == "H":
        x = input("Piano di studi esterno creato...")
    
    crea_attivita([COD_UNI_EXT, "Ricerca", "3"])
    if char_input == "H":
        x = input("Attività esterna creata...")
    ###################################################################################


    ################### CREAZIONE STUDENTE E IMMATRICOLAZIONE #####################
    crea_studente([COD_STUDENTE, "Mario", "Rossi"])
    if char_input == "H":
        x = input("Studente creato...")

    if char_input == "A":
        IMMATRICOLA_START_TIME = time.time()

    immatricola([COD_STUDENTE, COD_UNI_INT, _CA, "Informatica", "TEST_PW"])
    if char_input == "H":
        x = input("Studente immatricolato all'università interna...")
    else:
        IMMATRICOLA_END_TIME = time.time() - IMMATRICOLA_START_TIME # type: ignore
    ###################################################################################


    ################### REGISTRAZIONE ESAMI CARRIERA INTERNA #####################
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
    #############################################################################


    ################### DOMANDA DI MOBILITA' ####################################
    if char_input == "A":
        DOMANDA_MOBILITA_START_TIME = time.time()
    domanda_mobilita([COD_UNI_INT, COD_UNI_EXT, COD_STUDENTE, "TEST_PW", "Analisi", "3", "", "Ricerca", "3", "", "R_INT", _CA, "R_EXT"])
    if char_input == "H":
        x = input("Domanda di mobilità inviata...")
    else:
        DOMANDA_MOBILITA_END_TIME = time.time() - DOMANDA_MOBILITA_START_TIME # type: ignore
    #############################################################################


    ################### REGISTRAZIONE UNIVERSITA' ESTERNA #####################
    if char_input == "A":
        IMMATRICOLA_EXT_START_TIME = time.time()

    immatricola([COD_STUDENTE, COD_UNI_EXT, _CA, "TEST_PW_EXT"])
    if char_input == "H":
        x = input("Studente registrato all'università esterna...")
    else:
        IMMATRICOLA_EXT_END_TIME = time.time() - IMMATRICOLA_EXT_START_TIME # type: ignore
    ###################################################################################
    

    ################### REGISTRAZIONE ESAMI E ATTIVITA' CARRIERA ESTERNA #####################
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
    if char_input == "H":
        x = input("Carriera esterna registrata...")
    ###########################################################################################


    ############################### EMISSIONE CREDENZIALE ###################################
    if char_input == "A":
        EMETTI_CREDENZIALE_START_TIME = time.time()

    emetti_credenziale([COD_UNI_EXT, COD_STUDENTE, "TEST_PW_EXT"])
    if char_input == "H":
        x = input("Credenziale emessa...")
    else:
        EMETTI_CREDENZIALE_END_TIME = time.time() - EMETTI_CREDENZIALE_START_TIME # type: ignore
    ###########################################################################################


    ############################### PRESENTAZIONE CREDENZIALE ###################################
    if char_input == "A":
        PRESENTA_CREDENZIALE_START_TIME = time.time()

    IC, FC = presenta_credenziale([COD_STUDENTE, COD_UNI_INT, 'TEST_PW', 'E', "Fisica", ""])
    if char_input == "H":
        x = input("Credenziale presentata all'università interna...")
    else:
        PRESENTA_CREDENZIALE_END_TIME = time.time() - PRESENTA_CREDENZIALE_START_TIME # type: ignore
    ###########################################################################################


    ############################### REVOCA CREDENZIALE ###################################
    # if char_input == "A":
    #     REVOCA_START_TIME = time.time()
    # revoca_credenziale([COD_STUDENTE, COD_UNI_EXT])
    # if char_input == "H":
    #     x = input("Credenziale revocata dall'università esterna...")
    # else:
    #     REVOCA_END_TIME = time.time() - REVOCA_START_TIME # type: ignore
    ###########################################################################################


    ############################### VERIFICA CREDENZIALE ###################################
    if char_input == "A":
        VERIFICA_START_TIME = time.time()

    verifica_credenziale([COD_STUDENTE, COD_UNI_INT])
  
    if char_input == "H":
        x = input("Credenziale verificata dall'università interna...")
    else:
        VERIFICA_END_TIME = time.time() - VERIFICA_START_TIME # type: ignore
    ###########################################################################################




    if char_input == "A":
        END_TIME = time.time() - START_TIME # type: ignore
        print(f"Tempo totale esecuzione: {END_TIME:.4f} secondi")
        print(f"Tempo certificazione università interna: {CERTIFICA_INT_END_TIME:.4f} secondi") #type: ignore
        print(f"Tempo certificazione università esterna: {CERTIFICA_EXT_END_TIME:.4f} secondi") #type: ignore
        print(f"Tempo immatricolazione università interna: {IMMATRICOLA_END_TIME:.4f} secondi") #type: ignore
        print(f"Tempo domanda mobilità: {DOMANDA_MOBILITA_END_TIME:.4f} secondi") #type: ignore
        print(f"Tempo immatricolazione università esterna: {IMMATRICOLA_EXT_END_TIME:.4f} secondi") #type: ignore
        print(f"Tempo emissione credenziale: {EMETTI_CREDENZIALE_END_TIME:.4f} secondi") #type: ignore
        print(f"Tempo presentazione credenziale: {PRESENTA_CREDENZIALE_END_TIME:.4f} secondi") #type: ignore
        print(f"Tempo verifica credenziale: {VERIFICA_END_TIME:.4f} secondi") #type: ignore

        print("La credenziale iniziale occupa:", asizeof.asizeof(IC), "bytes")
        print("La credenziale finale occupa:", asizeof.asizeof(FC), "bytes")


elif char_input == "C":
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
else:
    print("Input non valido")
