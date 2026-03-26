# 1) Use Case Diagram

Attach your use case diagram as an image under `../data/img/` and link it here:

- `![](../data/img/use-case-diagram.png)`

Also, make sure to include the JSON source file downloaded from the UML Modeler used to draw the diagram in the `../data/` folder.

# 2) Use Case Narratives

Add one narrative for each use case shown in the diagram.
  
| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      | 01                            |
| Scope                   | piattaforma Participium                            |
| Level                   | User goal                            |
| Intention in Context    | Registrazione                            |
| Primary actor           | Cittadino non registrato / non loggato                            |
| Supporting actors       | Servizio di autenticazione (STK-5), Mail server (STK-7)  |
| Stakeholders' interests | **Cittadino non registrato (STK-1)**: Vuole creare un account per poter inserire segnalazioni. |
| Precondition            | - |
| Minimum guarantees      |Nessun dato personale viene persistito in caso di registrazione non completata. Le credenziali (password) non vengono mai salvate nei database di Participium. |
| Success guarantees      | L'utente dispone di un account attivo e verificato sulla piattaforma. L'utente può effettuare il login. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente chiede di potersi registrare.<br>2. L'utente inserisce username, nome, cognome, indirizzo email e password.<br>3. L'utente conferma e invia il modulo di registrazione.<br>4. Il sistema crea l'account in stato "non verificato" e invia un'email con link di verifica [FR-01].<br>5. L'utente clicca sul link di verifica ricevuto via email.<br>6. Il sistema attiva l'account [FR-01].<br>7. Il sistema propone al cittadino di completare il profilo: caricare opzionalmente una foto profilo [FR-05] e impostare le preferenze di notifica email [FR-04].<br>8. Il cittadino configura le preferenze desiderate.<br>9. Il sistema salva le impostazioni selezionate [FR-04] [FR-05].<br>10. L'utente viene reindirizzato alla piattaforma come utente autenticato. |
| Extensions              | 3a. L'utente annulla la registrazione.<br>3a.1 Il sistema non crea l'account, il caso d'uso termina con un fallimento.<br>4a. I dati inseriti non sono validi o sono incompleti.<br>4a.1 Il sistema mostra gli errori e il caso d'uso riprende dal punto 2.<br>8a. Il cittadino salta la configurazione del profilo.<br>8a.1 Il sistema mantiene le impostazioni predefinite e il caso d'uso riprende dal punto 10. |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      | 02                          |
| Scope                   | piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Recupero password           |
| Primary actor           | Cittadino registrato (non loggato) |
| Supporting actors       | Servizio di autenticazione (STK-5), Mail server (STK-7) |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole recuperare l'accesso al proprio account.|
| Precondition            | L'utente possiede un account sulla piattaforma. |
| Minimum guarantees      | Le credenziali precedenti rimangono valide fino al completamento del reset. |
| Success guarantees      | L'utente ha impostato una nuova password e può effettuare il login. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente accede alla pagina di recupero password.<br>2. L'utente inserisce l'indirizzo email associato al proprio account.<br>3. L'utente conferma e invia la richiesta.<br>4. Il sistema verifica l'email e genera un link di reset [FR-02].<br>5. Il sistema invia un'email con il link di reset all'indirizzo fornito [FR-02].<br>6. L'utente accede al link di reset ricevuto via email.<br>7. L'utente inserisce e conferma la nuova password.<br>8. Il sistema aggiorna le credenziali [FR-02].<br>9. L'utente viene reindirizzato alla pagina di login. |
| Extensions              | 3a. L'utente annulla il recupero.<br>3a.1 Il sistema non invia nessuna email, il caso d'uso termina con un fallimento.<br>7a. Le password inserite non coincidono o non rispettano i requisiti di sicurezza.<br>7a.1 Il sistema mostra gli errori e il caso d'uso riprende dal punto 7. |



| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      | 03                          |
| Scope                   | piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Login                       |
| Primary actor           | Utente registrato (Cittadino STK-2, Operatore comunale STK-3) |
| Supporting actors       | Servizio di autenticazione (STK-5) |
| Stakeholders' interests | **Cittadino (STK-2)**: vuole accedere alla propria area riservata per gestire le segnalazioni. **Operatore comunale (STK-3)**: vuole accedere alla dashboard interna per gestire le pratiche. |
| Precondition            | L'utente possiede un account attivo e verificato sulla piattaforma. |
| Minimum guarantees      | -|
| Success guarantees      | L'utente dispone di una sessione autenticata attiva con i permessi corrispondenti al proprio ruolo. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente accede alla pagina di login.<br>2. L'utente inserisce username e password.<br>3. L'utente conferma e invia il modulo di login.<br>4. Il sistema verifica le credenziali tramite il servizio di autenticazione [FR-03].<br>5. Il sistema crea una sessione autenticata [FR-03].<br>6. L'utente viene reindirizzato all'area riservata corrispondente al proprio ruolo. |
| Extensions              | 3a. L'utente annulla il login.<br>3a.1 Il sistema non crea nessuna sessione, il caso d'uso termina con un fallimento.<br>4a. Le credenziali inserite non sono corrette.<br>4a.1 Il sistema mostra un messaggio di errore generico e il caso d'uso riprende dal punto 2. |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      | 04                          |
| Scope                   | piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Logout                      |
| Primary actor           | Utente registrato (Cittadino STK-2, Operatore comunale STK-3) |
| Supporting actors       | Servizio di autenticazione (STK-5) |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole terminare la sessione in modo sicuro per tutelare i propri dati. **Operatore comunale (STK-3)**: vuole disconnettersi al termine del turno di lavoro. |
| Precondition            | L'utente è autenticato sulla piattaforma. |
| Minimum guarantees      | - |
| Success guarantees      | La sessione dell'utente è terminata e nessun dato personale rimane accessibile senza nuova autenticazione. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente richiede il logout.<br>2. Il sistema invalida la sessione autenticata [FR-03].<br>3. L'utente viene reindirizzato alla pagina pubblica della piattaforma. |
| Extensions              | - |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      | 05                          |
| Scope                   | piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Aggiornamento profilo       |
| Primary actor           | Cittadino registrato (STK-2) |
| Supporting actors       | -                           |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole personalizzare il proprio profilo e gestire le preferenze di notifica. |
| Precondition            | L'utente è autenticato sulla piattaforma. |
| Minimum guarantees      | Le modifiche non confermate non vengono persistite. |
| Success guarantees      | Le nuove impostazioni del profilo sono attive. |
| Trigger                 | - |
| Main success scenario   | 1. Il cittadino accede alla sezione del proprio profilo. Il sistema mostra le impostazioni correnti.<br>2. Il cittadino apporta le modifiche desiderate: aggiorna le preferenze di notifica email [FR-04] e/o carica una nuova foto profilo [FR-05].<br>3. Il cittadino conferma e salva le modifiche.<br>4. Il sistema aggiorna il profilo con le nuove impostazioni [FR-04] [FR-05].<br>5. Il sistema mostra la conferma di avvenuto aggiornamento. |
| Extensions              | 3a. Il cittadino annulla le modifiche.<br>3a.1 Il sistema non persiste nessuna modifica, il caso d'uso termina.|

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      | 06                          |
| Scope                   | piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Inserimento segnalazione    |
| Primary actor           | Cittadino registrato (STK-2) |
| Supporting actors       | OpenStreetMap (STK-8) |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole segnalare un problema urbano. **Operatore comunale (STK-3)**: vuole ricevere segnalazioni con posizione, categoria e foto. **Comune di Torino (STK-9)**: vuole aumentare la partecipazione civica e ricevere dati sulla situazione urbana. |
| Precondition            | L'utente è autenticato sulla piattaforma. |
| Minimum guarantees      | In caso di fallimento, nessuna segnalazione viene persistita. |
| Success guarantees      | La segnalazione è pubblicata sulla piattaforma in stato "Pending Approval" |
| Trigger                 | - |
| Main success scenario   | 1. Il cittadino accede al modulo di inserimento segnalazione.<br>2. Il cittadino seleziona la posizione del problema sulla mappa [FR-06].<br>3. Il cittadino inserisce titolo e descrizione e seleziona una categoria dalla lista predefinita [FR-06].<br>4. Il cittadino allega opzionalmente fino a 3 foto, compresse automaticamente lato client [FR-06].<br>5. Il cittadino sceglie se rendere la segnalazione anonima [FR-07].<br>6. Il cittadino conferma e invia la segnalazione.<br>7. Il sistema valida i dati e pubblica la segnalazione in stato "Pending Approval" [FR-06].<br>8. Il sistema mostra la conferma di avvenuta creazione della segnalazione. |
| Extensions              | 6a. Il cittadino annulla l'inserimento.<br>6a.1 Il sistema scarta i dati, nessuna segnalazione viene creata, il caso d'uso termina con un fallimento.<br>7a. I campi obbligatori (posizione, titolo, categoria) non sono stati compilati.<br>7a.1 Il sistema evidenzia i campi mancanti e il caso d'uso riprende dal punto 2. |

# 3) Traceability Table

| UC ID | REQ ID |
| :---- | :----- |
| UC-XX | FR-XX  |
