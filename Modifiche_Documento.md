WP4 PER INTERO
## 17/07
E' stato individuato un ordine col quale studente e università utilizzano i nonce per autenticarsi l'un l'altro senza esporre informazioni che potrebbero essere utilizzate in un replay attack:
* Lo studente invia sia timestamp che numero casuale, in cifrato
* L'università risponde o con l'uno con l'altro, esponendolo, in chiaro ma firmato
* Lo studente invia l'altra informazione, in cifrato, autenticandosi e evitando replay attacks, eventualmente allegando la chiave simmetrica attraverso la quale comunicare

E' stato commesso un errore durante la progettazione: non è possibile alterare a piacimento l'ID di un blocco, siccome questo è ottenuto mediante l'hash dello stesso. Per cui si corregge il documento (in particolare, la parte dove si definisce come si rileva l'eventuale eliminazione di una certificazione, che viene alterata per supportare questa modifica).

## 21/07 
Da "I meccanismi di crittografia più comuni" a "I meccanismi di crittografia più recenti" in Attacco con credenziale nota

Si modifica il protocollo di autenticazione con due nounce piuttosto che due timestamp e anticipato di uno durante la comunicazione dello schema simmetrico.