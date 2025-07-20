import json
import os
import secrets
import sys
import time

from algorithms import *
from communication import Certificate
from constants import DATA_DIRECTORY, MAXIMUM_TIMESTAMP_DIFFERENCE, RANDOM_NUMBER_MAX, STUDENTS_FOLDER, _registra_attivita, _registra_esame
from communication import Message, User
from actors import *

class Attacker(User):
    def __init__(self, name: str):
        super().__init__(name)

    @staticmethod
    def load_from_json(data: dict):
        return User.load_from_json(data)

def _intercept_message(sender: User, receiver: User, message: Message, encrypt: bool = True, sign: bool = False) -> Message:
        """
        Funzione per intercettare i messaggi tra lo studente e l'università.
        L'attaccante può leggere i messaggi e modificarli se necessario.
        """
        if encrypt: # Se il messaggio viene inviato già cifrato, l'attaccante non è in grado di decifrarlo
            mex = sender._keys[receiver.get_code()].encrypt(message) # Caso dello studente che invia un messaggio cifrato all'università
        else: # Se il messaggio non viene cifrato, l'attaccante può leggerlo
            mex = message
        if sign: # Se il messaggio viene firmato, l'attaccante non è in grado di forgiare una firma valida quando modifica il contenuto
            mex = sender._keys[sender.get_code()].sign(mex) # Caso dell'università che invia un messaggio firmato allo studente
        return mex

def _immatricola(args:list[str]=[]):
    """
        Algoritmo di immatricolazione dello studente presso l'università. Lo studente deve fornire una password per autenticarsi in futuro.
        Tutti i messaggi in uscita dallo studente vengono cifrati con la chiave pubblica dell'università, quelli in entrata vengono solo firmati con la chiave privata dell'università.
        L'università deve essere certificata da una CA, e lo studente deve conoscere la chiave pubblica della CA per verificare il certificato dell'università.
        VIOLAZIONE: Vi è un attaccante che intercetta i messaggi che transitano tra lo studente e l'università ospitante, inoltre può alterarli o inviarne di altri.
        Args:
            - arg1: Codice dello studente
            - arg2: Codice dell'università
            - arg3: Nome della CA
            - arg4: Piano di studi scelto
            - arg5: Password scelta dallo studente

    """
    ATTACKER = Attacker("ATT")
    students, universities, CAs = lettura_dati()[0:3] # type: ignore
    if len(args) > 0:
        student_name = args[0]
    else:
        student_name = input("Inserisci il nome dello studente: ")
    while student_name not in students:
        print("Lo studente non esiste.")
        student_name = input("Inserisci il nome dello studente: ")
    
    if len(args) > 1:
        university_name = args[1]
    else:
        university_name = input("Inserisci il nome dell'università: ")
    while university_name not in universities:
        print("L'università non esiste.")
        university_name = input("Inserisci il nome dell'università: ")

    
    if len(args) > 2:
        ca_name = args[2]
    else:
        ca_name = input("Inserisci il nome della CA: ")
    while ca_name not in CAs:
        print("La CA non esiste.")
        ca_name = input("Inserisci il nome di una CA dove la chiave pubblica dell'università è registrata, o premi invio per prenderne una disponibile")

    
    student:Student = students[student_name]
    university:University = universities[university_name]
    ca:CA = CAs[ca_name]
    
    #* 1 Lo studente cerca la chiave pubblica dell'università dalla CA, ha prima bisogno della chiave pubblica della CA
    public_key = ca.get_public_key()
    if public_key is None:
        raise ValueError(f"La CA {ca_name} non ha una chiave pubblica registrata.")

    #* 2 Lo studente utilizza la chiave pubblica della CA per verificare che certificato che riceve dalla CA sia valido
    uni_cert = ca.get_user_certificate(university)
    if uni_cert is None:
        raise ValueError(f"La CA {ca_name} non ha un certificato registrato per l'università {university_name}.")
    if not isinstance(uni_cert, Certificate):
        raise TypeError(f"Il certificato dell'università deve essere di tipo Certificate, ma è di tipo {type(uni_cert)}")
    
    if not public_key.verify(uni_cert):
        raise ValueError(f"Il certificato dell'università {university_name} non è valido: la firma non corrisponde.")
    print("Certificato dell'università verificato con successo.")
    uni_public_key = uni_cert.read_key()
    ATTACKER.add_key(university, uni_public_key)  # L'attaccante conosce la chiave pubblica dell'università


    #* 3 Lo studente si salva la chiave pubblica dell'università e la utilizza per comunicare con essa
    student.add_key(university, uni_public_key)
    i = 3
    if university.is_incoming_student(student):
        study_plan = "ext"
    else:
        study_plans = university.get_study_plans()
        if study_plans is None or len(study_plans) == 0:
            raise ValueError("L'università non ha piani di studio disponibili.")
        if len(args) > i:
            study_plan = args[i]
            i+=1
        else:
            study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")
        while study_plan not in study_plans:
            print(f"Il piano di studi {study_plan} non esiste nell'università {university_name}.")
            study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")

    student_initial_timestamp = time.time()
    RANDOM_NUMBER0 = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 9999 non basato su timestamp
    RANDOM_NUMBER1 = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 9999 non basato su timestamp

    message_data = {
        "name": student.get_name(),
        "surname": student.get_surname(),
        "code": student.get_code(),
        "timestamp": student_initial_timestamp,
        "text": "Immatricolazione",
        "study_plan": study_plan,
        # "email": "..." # Si potrebbe considerare in futuro l'utilizzo di una email come scenario 2FA
        "nonce0": RANDOM_NUMBER0,
        "nonce1": RANDOM_NUMBER1
    }

    message = Message(json.dumps(message_data))
    # student.send(university, message, sign=False) #! INTERCETTATO
    intercepted_message = _intercept_message(student, university, message, encrypt=True)
    print("L'attaccante ha intercettato il messaggio, tuttavia non ha modo di inferire il contenuto cifrato. I numeri casuali che l'utente ha utilizzato non sono visibili, e se non dipendono dal tempo, non sono prevedibili. L'attaccante potrebbe al più alterare il messaggio, ma non avrebbe senso siccome non potrebbe inferire altro")
    university._receive(student, intercepted_message, decrypt=True, verify=False)  # L'università riceve il messaggio e lo decifra con la propria chiave privata
    #* 4 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di definire una password con la quale potrà autenticarsi successivamente
    #! OLD Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    #* Per evitare replay attack, l'università chiede allo studente di fornire l'altro nonce casuale
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    first_received_timestamp = received_data["timestamp"]
    # Controlla che la differenza del timestamp non superi la costante MAXIMUM_TIMESTAMP_DIFFERENCE
    if abs(time.time() - first_received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    uni_message = {
        "text": f"Benvenuto {received_data['name']} {received_data['surname']}, per favore fornisci una password per autenticarti in futuro, inoltre, invia il l'altro nonce e il timestamp attuale",
        "nonce": received_data["nonce0"],
        "timestamp": time.time()
    }
    #university.send(student, Message(json.dumps(uni_message)), encrypt=False, sign=True) #! INTERCETTATO
    intercepted_uni_message = _intercept_message(university, student, Message(json.dumps(uni_message)), encrypt=False, sign=True)
    INTERCEPTED_FIRST_NONCE = received_data["nonce0"]
    # ! Si presume che il secondo nonce sia indipendente dal primo e dal tempo, quindi l'attaccante non può prevederlo
    print("L'attaccante ha intercettato il messaggio dell'università, che naviga in chiaro ma è firmato, quindi l'attaccante non può alterarlo senza che lo studente se ne accorga. Può tuttavia leggere il contenuto del messaggio. L'unica informazione che inferisce è il primo nonce: se l'altro nonce è stocasticamente dipendente dal tempo e dal primo, l'attaccante potrebbe predirlo.")
    student._receive(university, intercepted_uni_message, decrypt=False, verify=True)
    #* 5 Lo studente riceve il messaggio e procede a definire una password
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())
    if received_data['nonce'] != RANDOM_NUMBER0:
        raise ValueError("Il nonce non corrisponde a quello inviato, possibile replay attack.")
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    if len(args) > i:
        password = args[i]
        i+=1
    else:
        password = input("Inserisci una password per autenticarti all'università: ")
    while not password:
        print("La password non può essere vuota.")
        password = input("Inserisci una password per autenticarti all'università: ")
    student.set_password(password, university) # Lo studente si ricorderà la password per usi futuri (viene salvata in student.json in chiaro a scopo didattico)
    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump({code: s.save_on_json() for code, s in students.items()}, f, indent=4)

    password_message = {
        "password": password,
        "timestamp": time.time(),
        "nonce": RANDOM_NUMBER1,
        "text": "Password di immatricolazione"
    }

    # student.send(university, Message(json.dumps(password_message)), sign=False) #! INTERCETTATO
    intercepted_password_message = _intercept_message(student, university, Message(json.dumps(password_message)), encrypt=False, sign=False)
    print("L'attaccante intercetta il messaggio dela password, non firmato ma cifrato, per cui non può leggerne il contenuto. Potrebbe alterarlo, ma non conosce il secondo nonce e quindi non potrebbe inviare un messaggio valido all'università.")
    PROBABILISTIC_SECOND_NONCE = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 9999
    attack_password_message = {
        "password": "Ciao sono l'attaccante, ho rubato la password dello studente",
        "timestamp": time.time(),
        "nonce": PROBABILISTIC_SECOND_NONCE,  # L'attaccante invia un nonce casuale, incrociando le dita
        "text": "Password di immatricolazione"
    }
    student.send(university, Message(json.dumps(attack_password_message)), sign=False)  #! ALTERATO
    #* 6 L'università riceve la password e la salva nel proprio database, immatricolando lo studente
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    if received_data['nonce'] != RANDOM_NUMBER1:
        raise ValueError("Il nonce ricevuto non corrisponde a quello originale, attacco fallito.")

    university.enroll_student(student, password, study_plan)
    print("Attacco riuscito, l'attaccante ha immatricolato lo studente con una password diversa. Lo studente non potrà autenticarsi in futuro, ma l'università non se ne accorgerà fino a quando l'attaccante accede al sistema con la password alterata.")

def _immatricola_OLD(args:list[str]=[]):
    """
        Algoritmo di immatricolazione dello studente presso l'università. Lo studente deve fornire una password per autenticarsi in futuro.
        Tutti i messaggi in uscita dallo studente vengono cifrati con la chiave pubblica dell'università, quelli in entrata vengono solo firmati con la chiave privata dell'università.
        L'università deve essere certificata da una CA, e lo studente deve conoscere la chiave pubblica della CA per verificare il certificato dell'università.

        VIOLAZIONE: Vi è un attaccante che intercetta i messaggi che transitano tra lo studente e l'università ospitante, inoltre può alterarli o inviarne di altri.
        Args:
            - arg1: Codice dello studente
            - arg2: Codice dell'università
            - arg3: Nome della CA
            - arg4: Piano di studi scelto
            - arg5: Password scelta dallo studente

    """

    students, universities, CAs = lettura_dati()[0:3] # type: ignore
    if len(args) > 0:
        student_name = args[0]
    else:
        student_name = input("Inserisci il nome dello studente: ")
    while student_name not in students:
        print("Lo studente non esiste.")
        student_name = input("Inserisci il nome dello studente: ")
    
    if len(args) > 1:
        university_name = args[1]
    else:
        university_name = input("Inserisci il nome dell'università: ")
    while university_name not in universities:
        print("L'università non esiste.")
        university_name = input("Inserisci il nome dell'università: ")

    
    if len(args) > 2:
        ca_name = args[2]
    else:
        ca_name = input("Inserisci il nome della CA: ")
    while ca_name not in CAs:
        print("La CA non esiste.")
        ca_name = input("Inserisci il nome di una CA dove la chiave pubblica dell'università è registrata, o premi invio per prenderne una disponibile")

    
    student:Student = students[student_name]
    university:University = universities[university_name]
    ca:CA = CAs[ca_name]
    

    ATTACKER = Attacker("ATT")
    
    #* 1 Lo studente cerca la chiave pubblica dell'università dalla CA, ha prima bisogno della chiave pubblica della CA
    public_key = ca.get_public_key()
    if public_key is None:
        raise ValueError(f"La CA {ca_name} non ha una chiave pubblica registrata.")

    #* 2 Lo studente utilizza la chiave pubblica della CA per verificare che certificato che riceve dalla CA sia valido
    uni_cert = ca.get_user_certificate(university)
    if uni_cert is None:
        raise ValueError(f"La CA {ca_name} non ha un certificato registrato per l'università {university_name}.")
    if not isinstance(uni_cert, Certificate):
        raise TypeError(f"Il certificato dell'università deve essere di tipo Certificate, ma è di tipo {type(uni_cert)}")
    
    if not public_key.verify(uni_cert):
        raise ValueError(f"Il certificato dell'università {university_name} non è valido: la firma non corrisponde.")
    print("Certificato dell'università verificato con successo.")
    uni_public_key = uni_cert.read_key()

    ATTACKER.add_key(university, uni_public_key)  # L'attaccante conosce la chiave pubblica dell'università

    #* 3 Lo studente si salva la chiave pubblica dell'università e la utilizza per comunicare con essa
    student.add_key(university, uni_public_key)
    i = 3
    if university.is_incoming_student(student):
        study_plan = "ext"
    else:
        study_plans = university.get_study_plans()
        if study_plans is None or len(study_plans) == 0:
            raise ValueError("L'università non ha piani di studio disponibili.")
        if len(args) > i:
            study_plan = args[i]
            i+=1
        else:
            study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")
        while study_plan not in study_plans:
            print(f"Il piano di studi {study_plan} non esiste nell'università {university_name}.")
            study_plan = input(f"Scegli un piano di studi tra {', '.join(study_plans.keys())}: ")

    student_initial_timestamp = time.time()
    random_number = secrets.randbelow(RANDOM_NUMBER_MAX)  # Numero casuale tra 0 e 999999 non basato su timestamp

    message_data = {
        "name": student.get_name(),
        "surname": student.get_surname(),
        "code": student.get_code(),
        "timestamp": student_initial_timestamp,
        "text": "Richiesta di immatricolazione",
        "study_plan": study_plan,
        # "email": "..." # Si potrebbe considerare in futuro l'utilizzo di una email come scenario 2FA
        "nonce": random_number
    }

    message = Message(json.dumps(message_data))
    # student.send(university, message, sign=False) #! INTERCETTATO
    intercepted_message = _intercept_message(student, university, message, encrypt=True)
    INITIAL_PROBABLE_TIMESTAMP = time.time()  # Timestamp probabile per l'attaccante, che non conosce il timestamp originale
    print(intercepted_message.get_content())
    print("L'attaccante non può decifrare il messaggio perché è cifrato con la chiave pubblica dell'università, potrebbe tentare di inferire il contenuto se conosce formato e studente, confrontandolo con altri messaggi, tuttavia non è a conoscenza del numero casuale")
    university._receive(student, intercepted_message, decrypt=True, verify=False)  # L'università riceve il messaggio e lo decifra con la propria chiave privata

    #* 4 L'università riceve il messaggio e lo decifra con la propria chiave privata,
    #* chiede quindi allo studente di definire una password con la quale potrà autenticarsi successivamente
    #* Inoltre, per evitare replay attack gli chiede di ripetere il timestamp originale
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    first_received_timestamp = received_data["timestamp"]
    # Controlla che la differenza del timestamp non superi la costante MAXIMUM_TIMESTAMP_DIFFERENCE
    if abs(time.time() - first_received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")

    uni_message = {
        "text": f"Benvenuto {received_data['name']} {received_data['surname']}, per favore fornisci una password per autenticarti in futuro, inoltre, ripeti il timestamp originale e l'attuale",
        "nonce": received_data["nonce"],
        "timestamp": time.time()
    }
    # university.send(student, Message(json.dumps(uni_message)), encrypt=False, sign=True) #! INTERCETTATO
    intercepted_uni_message = _intercept_message(university, student, Message(json.dumps(uni_message)), encrypt=False, sign=True)
    INTERCEPTED_INITIAL_NONCE = json.loads(intercepted_uni_message.get_content())["nonce"]

    print(intercepted_uni_message.get_content())
    print("L'attaccante può leggere il messaggio, ma non può alterarlo senza che lo studente se ne accorga, perché è firmato con la chiave privata dell'università, tuttavia, sa che il prossimo messaggi in arrivo dallo studente conterrà la sua password")
    student._receive(university, intercepted_uni_message, decrypt=False, verify=True)

    #* 5 Lo studente riceve il messaggio e procede a definire una password
    received_message = student.get_last_message()
    received_data = json.loads(received_message.get_content())
    if received_data['nonce'] != random_number:
        raise ValueError("Il nonce non corrisponde a quello inviato, possibile replay attack.")
    received_timestamp = received_data['timestamp']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
    
    if len(args) > i:
        password = args[i]
        i+=1
    else:
        password = input("Inserisci una password per autenticarti all'università: ")
    while not password:
        print("La password non può essere vuota.")
        password = input("Inserisci una password per autenticarti all'università: ")
    student.set_password(password, university) # Lo studente si ricorderà la password per usi futuri (viene salvata in student.json in chiaro a scopo didattico)
    with open(os.path.join(DATA_DIRECTORY, STUDENTS_FOLDER, "students.json"), 'w') as f:
        json.dump({code: s.save_on_json() for code, s in students.items()}, f, indent=4)

    password_message = {
        "password": password,
        "timestamp": time.time(),
        "nonce": student_initial_timestamp,
        "text": "Password di immatricolazione"
    }

    # student.send(university, Message(json.dumps(password_message)), sign=False) #! INTERCETTATO
    intercepted_password_message = _intercept_message(student, university, Message(json.dumps(password_message)), encrypt=True, sign=False)
    
    print(intercepted_password_message.get_content())
    print("L'attaccante non può decifrare il messaggio perché è cifrato con la chiave pubblica dell'università, non può inferire alcuna informazione sulla password, ma può alterare il messaggio, tuttavia non conosce il timestamp originale, ma solo il nonce che venne inviato all'inizio della comunicazione. Tuttalpiù, potrebbe tentare variando il timestamp, ma la probbilità di successo è relativamente bassa (sarebbe possibile implementare un secondo nonce casuale per aumentare la sicurezza)")
    print("Lo studente tenta di rispondere all'università con una password nuova e un timestamp simile a quello iniziale:")
    new_altered_message = {
        "password": "nuova_password",
        "timestamp": time.time(),
        "nonce": INITIAL_PROBABLE_TIMESTAMP,
        "text": "Password di immatricolazione"
    }
    attacker_message = ATTACKER._keys[university.get_code()].encrypt(Message(json.dumps(new_altered_message)))  
    university._receive(student, attacker_message, decrypt=True, verify=False)  # L'università riceve il messaggio e lo decifra con la propria chiave privata
    #* 6 L'università riceve la password e la salva nel proprio database, immatricolando lo studente
    received_message = university.get_last_message()
    received_data = json.loads(received_message.get_content())
    received_timestamp = received_data['nonce']
    if abs(time.time() - received_timestamp) > MAXIMUM_TIMESTAMP_DIFFERENCE:
        raise ValueError("La differenza di timestamp supera il limite consentito, possibile replay attack.")
        
    if received_timestamp != first_received_timestamp:
        raise ValueError("Il timestamp ricevuto non corrisponde a quello originale, attacco fallito.")
    else:
        print("L'università ha immatricolato lo studente con successo, assegnandoli la password inventata dall'attaccante: l'attacco ha avuto successo e ora è in grado di accedere ai servizi universitari come studente.")
    university.enroll_student(student, password, study_plan)
    

def intercettatore_ospitante_studente():
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


    _immatricola([COD_STUDENTE, COD_UNI_INT, _CA, "Informatica", "TEST_PW"])
