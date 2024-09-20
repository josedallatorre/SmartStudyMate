# SmartStudyMate

## Progetto per il corso di Sistemi Informativi e DataWarehouse dell'anno 2023/2024

### Specifiche del progetto
Il progetto richiedeva la creazione di un prodotto che consentisse agli studenti di accedere ai canali Teams dei vari corsi e di selezionare un corso specifico. Successivamente, il corso selezionato sarebbe stato utilizzato per recuperare tutte le videolezioni salvate tra i materiali del corso. Queste videolezioni vengono poi elaborate per generare delle dispense. Le dispense devono coprire tutti gli argomenti del corso, essere divise in capitoli, includere domande per ciascun capitolo e, infine, fornire le risposte a tali domande.
Per poter realizzare questo prodotto è stato necessario dividere in 2 la realizzazione del progetto:
• Recupero dei video da Teams;
• Generazione delle dispense a partire dai video ed invio delle dispense generate.
Per completare la prima fase, è stato necessario richiedere a Teams l’accesso al servizio di autenticazione. Successivamente, è stato richiesto all’università l’accesso ai vari corsi a cui lo studente è iscritto su Teams. Una volta ottenuti i dati sui corsi, le lezioni collegate sono state scaricate.
Per la seconda fase, è stato necessario cercare un modello per la trascrizione delle lezioni e un modello per la generazione delle dispense. Per la trascrizione è stato utilizzato Whisper di OpenAI, mentre per la generazione delle dispense è stato impiegato Qwen1.5-14B-Chat.
Infine, il tutto è stato integrato in un’interfaccia che consente agli utenti di interagire con il sistema in modo semplice e intuitivo.

### Requisiti del sistema
GPU: 30GB
CPU: Nessuna richiesta particolare
Tipologia di scheda grafica: Nvidia
Per la parte di recupero delle lezioni è necessario installare nella propria macchina Docker in modo tale da poter costruire l’ambiente adatto.


### Installazione ed avvio di Smart Study Mate

Le procedure di installazione ed avvio di Smart Study Mate sono le seguenti:
Fare il download della repo digitando sul terminale `git https://github.com/josedallatorre/SmartStudyMate.git`.

Copiare i file .env.sample `cp server/.env.sample server/.env` e `cp core/.env.sample core/.env`.

Modificare i parametri dell'env in server in base agli ID ottenuti su [Microsoft Entra](https://entra.microsoft.com/#home) e all'architettura (leggere di seguito).

Modificare i parametri dell'env in core in base alla password e alla email di Google con cui verrà inviata la dispensa.

Nel caso in ci sia solo una macchina: `docker compose -f compose.dev.yaml up`.

Nel caso ci siano due macchine: `docker compose up` nella macchina che non dispone di GPU e 
`docker run -it -v ./core:/home/app -p 5000:5000 --gpus all josedallatorre/ssm-core` su quella che dispone di GPU.
