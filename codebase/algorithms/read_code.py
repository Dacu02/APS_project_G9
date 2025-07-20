def read_code(prompt: str, input_str:str|None=None) -> str:
    """
        Funzione per leggere un codice da input, con un prompt personalizzato.
        Ritorna il codice inserito.
    """
    if input_str:
        code = input_str
    else:
        code = input(prompt)
    while not code.isdigit() or len(code) != 3:
        print("Il codice deve essere un numero di 3 cifre.")
        code = input(prompt)
    return code