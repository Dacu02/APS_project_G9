## 17/07
E' stato individuato un ordine col quale studente e università utilizzano i nonce per autenticarsi l'un l'altro senza esporre informazioni che potrebbero essere utilizzate in un replay attack:
* Lo studente invia sia timestamp che numero casuale, in cifrato
* L'università risponde o con l'uno con l'altro, esponendolo, in chiaro ma firmato
* Lo studente invia l'altra informazione, in cifrato, autenticandosi e evitando replay attacks