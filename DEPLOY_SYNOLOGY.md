# Guida al Deployment su Synology NAS

Questa guida ti aiuterà a installare l'applicazione Network Monitor sul tuo NAS Synology utilizzando Container Manager (Docker).

## Novità: Configurazione Automatica

Abbiamo aggiornato l'applicazione per usare un **Reverse Proxy interno**.
**Non devi più configurare manualmente l'indirizzo IP del NAS.** L'applicazione funzionerà automaticamente ovunque la installi.

## 1. Trasferimento su NAS

1.  Crea una cartella sul tuo NAS, ad esempio `/docker/network-monitor`.
2.  Copia **tutti** i file e le cartelle del progetto (inclusi `backend`, `frontend`, `docker-compose.yml`) in questa cartella.

## 2. Avvio con Container Manager

1.  Apri **Container Manager** sul tuo Synology.
2.  Vai nella scheda **Progetto** (Project).
3.  Clicca su **Crea**.
4.  Compila i campi:
    *   **Nome progetto**: `network-monitor`
    *   **Percorso**: Seleziona la cartella `/docker/network-monitor` dove hai copiato i file.
    *   **Origine**: Seleziona "Crea docker-compose.yml" (il sistema rileverà automaticamente il file presente nella cartella).
5.  Clicca **Avanti** -> **Avanti** -> **Fine**.

Il NAS inizierà a scaricare le immagini base e a costruire i container. La prima volta potrebbe impiegare alcuni minuti.

## 3. Accesso all'Applicazione

Una volta che i container sono avviati (pallino verde), puoi accedere:

*   **Frontend (Dashboard)**: `http://IP-NAS:3000`
    *   *Ora il frontend contatterà automaticamente il backend senza bisogno di configurazioni extra.*
*   **InfluxDB**: `http://IP-NAS:8086`

## Risoluzione Problemi

*   **Porte occupate**: Se ricevi un errore che le porte sono già in uso, modifica il file `docker-compose.yml` cambiando la porta sinistra.
    Esempio per cambiare la porta del frontend a 3005:
    ```yaml
    ports:
      - "3005:80"
    ```
