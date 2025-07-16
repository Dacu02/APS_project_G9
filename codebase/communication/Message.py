class Message:
    """
        Classe che rappresenta un messaggio, il quale contiene del testo.
        Contiene un campo per il contenuto del messaggio e uno opzionale per la firma, oppure per token.
    """
    def __init__(self, content: str, signature: str | None = None):
        self._content = content
        self._signature = signature

    def get_content(self) -> str:
        return self._content

    def get_signature(self) -> str | None:
        return self._signature
    