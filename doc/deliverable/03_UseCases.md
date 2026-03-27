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

| Use Case                | Inserimento segnalazione |
|:------------------------|:----------------------------|
| ID                      | UC-06                          |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Creare una segnalazione specificando: posizione sulla mappa, titolo, descrizione, categoria da lista predefinita e fino a 3 foto     |
| Primary actor           | Cittadino registrato |
| Supporting actors       | OpenStreetMap (STK-8) |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole segnalare un problema urbano. **Operatore comunale (STK-3)**: vuole ricevere segnalazioni con posizione, categoria e foto. **Comune di Torino (STK-9)**: vuole aumentare la partecipazione civica e ricevere dati sulla situazione urbana. |
| Precondition            | L'utente è autenticato. L'utente non ha superato il limite massimo di segnalazioni giornaliere (Rate-limiting)  |
| Minimum guarantees      | In caso di fallimento, nessuna segnalazione viene persistita. |
| Success guarantees      | La segnalazione è pubblicata sulla piattaforma in stato "Pending Approval" |
| Trigger                 | Il cittadino riscontra un problema urbano e decide di comunicarlo al Comune. |
| Main success scenario   | 1. Il cittadino accede al modulo di inserimento segnalazione.<br>2. Il cittadino seleziona la posizione del problema sulla mappa [FR-06].<br>3. Il cittadino inserisce titolo e descrizione e seleziona una categoria dalla lista predefinita [FR-06].<br>4. Il cittadino allega opzionalmente fino a 3 foto, compresse automaticamente lato client [FR-06].<br>5. Il cittadino sceglie se rendere la segnalazione anonima [FR-07].<br>6. Il cittadino conferma e invia la segnalazione.<br>7. Il sistema valida i dati e pubblica la segnalazione in stato "Pending Approval" [FR-06].<br>8. Il sistema mostra la conferma di avvenuta creazione della segnalazione. |
| Extensions              | 6a. Il cittadino annulla l'inserimento.<br>6a.1 Il sistema scarta i dati, nessuna segnalazione viene creata, il caso d'uso termina con un fallimento.<br>7a. I campi obbligatori (posizione, titolo, categoria) non sono stati compilati.<br>7a.1 Il sistema evidenzia i campi mancanti e il caso d'uso riprende dal punto 2. | 


| Use Case                | Consultazione proprie segnalazioni                            |
|:------------------------|:----------------------------|
| ID                      | UC-07                          |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Visualizzare in dettaglio le segnalazioni inviate personalmente e quelle seguite.|
| Primary actor           | Cittadino registrato |
| Supporting actors       | -                           |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole monitorare lo stato di avanzamento delle proprie segnalazioni e di quelle seguite senza dover contattare direttamente gli operatori. **Comune di Torino (STK-9)**: vuole garantire trasparenza ai cittadini sul trattamento delle pratiche aperte. |
| Precondition            | L'utente è autenticato sulla piattaforma. |
| Minimum guarantees      | L'utente visualizza esclusivamente le segnalazioni associate al proprio account e quelle che ha scelto di seguire. |
| Success guarantees      | L'utente dispone di una vista aggiornata di tutte le segnalazioni di suo interesse con relativo stato corrente. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente accede alla sezione delle proprie segnalazioni.<br>2. Il sistema recupera e mostra in formato tabellare le segnalazioni create dall'utente e quelle seguite, con titolo, data, categoria e stato corrente [FR-10] [FR-11].<br>3. Il caso d'uso termina con successo. |
| Extensions              | 2a. L'utente non ha ancora creato né seguito nessuna segnalazione.<br>2a.1 Il sistema mostra un elenco vuoto con un messaggio informativo e il caso d'uso termina con successo. |


| Use Case                |  Seguire una segnalazione                       |
|:------------------------|:----------------------------|
| ID                      |         UC-08                 |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User Goal                   |
| Intention in Context    |  Iscriversi ad una segnalazione creata da un altro utente per ricevere aggiornamenti             |
| Primary actor           |          Cittadino registrato                  |
| Supporting actors       |          -                  |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole ricevere aggiornamenti sulle segnalazioni di proprio interesse senza doverle creare nuovamente. |
| Precondition            |           L'utente è autenticato e visualizza il dettaglio di una segnalazione non creata da lui.                 |
| Minimum guarantees      | - |
| Success guarantees      |              L'utente risulta follower della segnalazione e riceverà le future notifiche.              |
| Trigger                 | - |
| Main success scenario   |            1. L'utente chiede di seguire la segnalazione attualmente visualizzata.<br>2. Il sistema registra la relazione di follow tra l'utente e la segnalazione [FR-10].<br>3. Il sistema aggiorna l'interfaccia confermando che la segnalazione è seguita. <br>Il caso d'uso termina con successo. |
|Extensions              |         2a. L'utente annulla l'operazione.<br>2a.1 Il sistema non registra il follow, il caso d'uso termina con un fallimento.                   |

| Use Case                |  Ricezione e visulizazione notifica                     |
|:------------------------|:----------------------------|
| ID                      | UC-09                          |
| Scope                   | Piattaforma Participium     |
| Level                   | Subfunction                 |
| Intention in Context    | Ricezione e visualizzazione notifica cambio stato |
| Primary actor           | Cittadino registrato |
| Supporting actors       | Servizio notifiche (STK-6), Mail server (STK-7) |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole essere informato tempestivamente sui cambi di stato delle segnalazioni proprie o seguite senza dover controllare attivamente la piattaforma. **Operatore comunale (STK-3)**: vuole ridurre le richieste dirette di aggiornamento da parte dei cittadini. |
| Precondition            | L'utente è autenticato sulla piattaforma. L'operatore Comunale cambia lo stato di una segnalazione |
| Minimum guarantees      | Il cambio di stato della segnalazione viene registrato nel sistema indipendentemente dall'esito della notifica. |
| Success guarantees      | L'utente è informato del cambio di stato e ha accesso al dettaglio della segnalazione associata. |
| Trigger                 | Il sistema registra un cambio di stato per una segnalazione creata o seguita dall'utente. |
| Main success scenario   | 1. Il sistema invia una notifica push all'utente tramite il servizio notifiche [FR-14].<br>2. Il sistema invia opzionalmente una notifica email, se abilitata dall'utente [FR-15].<br>3. L'utente clicca sulla notifica ricevuta.<br>4. Il sistema marca la notifica come letta e reindirizza l'utente alla pagina di dettaglio della segnalazione. Il caso d'uso termina con successo. |
| Extensions              | 1a. Il servizio notifiche non è raggiungibile.<br>1a.1 Il sistema registra il fallimento della notifica push; il cambio di stato rimane comunque persistito.<br>2a. L'utente ha disabilitato le notifiche email [FR-04].<br>2a.1 Il sistema salta l'invio email e il caso d'uso termina con successo. |

| Use Case                |  Invio messaggio a operatore                      |
|:------------------------|:----------------------------|
| ID                      |         UC-10                |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User goal                  |
| Intention in Context    |  Inviare una comunicazione diretta all'operatore incaricato per fornire chiarimenti            |
| Primary actor           |          Cittadino registrato                   |
| Supporting actors       |          -               |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole fornire dettagli aggiuntivi o richiedere chiarimenti sulla propria segnalazione direttamente all'operatore. **Operatore comunale (STK-3)**: vuole ricevere informazioni aggiuntive dai cittadini per gestire le segnalazioni in modo più accurato ed efficiente. |
| Precondition            |           L'utente è autenticato.               |
| Minimum guarantees      | -              |
| Success guarantees      |              Il messaggio arriva all'operatore che può visualizzarlo nella dashboard interna.              |
| Trigger                 |  - |
| Main success scenario   |     1. L'utente inserisce il testo del messaggio e chiede di inviarlo.<br>2. Il sistema valida il contenuto del messaggio.<br>3. Il sistema salva il messaggio associandolo alla segnalazione e innesca la notifica per l'operatore [FR-16].<br>4. Il sistema aggiorna lo storico chat mostrando il nuovo messaggio inviato.<br>Il caso d'uso termina con successo. |
|Extensions              |         2a. Il testo del messaggio è vuoto.<br>2a.1 Il sistema mostra un errore, il caso d'uso riprende dal punto 1.                   |

| Use Case                |  Visualizzazione segnalazioni su mappa                      |
|:------------------------|:----------------------------|
| ID                      |         UC-11                |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User goal                   |
| Intention in Context    |  Esplorare sulla mappa i problemi urbani segnalati in città            |
| Primary actor           |          Cittadino registrato   e Cittadino non registrato             |
| Supporting actors       |          OpenStreetMap (STK-8)               |
| Stakeholders' interests | **Cittadino non registrato (STK-1)**: vuole esplorare visivamente i problemi urbani nel proprio quartiere senza doversi registrare. **Cittadino registrato (STK-2)**: vuole visualizzare sulla mappa le segnalazioni attive per monitorare la propria zona. **Comune di Torino (STK-9)**: vuole garantire trasparenza pubblica sulla situazione urbana del territorio. |
| Precondition            |           -               |
| Minimum guarantees      | In caso di indisponibilità della mappa, le segnalazioni rimangono sempre consultabili tramite la vista tabellare. |
| Success guarantees      |    I marker delle segnalazioni attive vengono renderizzati correttamente sulla mappa                        |
| Trigger                 | -                   |
| Main success scenario   |     1. L'utente chiede di visualizzare la mappa pubblica.<br>2. Il sistema richiede ed utilizza il servizio di  OpenStreetMap.<br>3. Il sistema interroga il database recuperando esclusivamente le segnalazioni negli stati attivi (Pending, Assigned, In Progress, Suspended) [FR-22].<br>4. Il sistema posiziona i marker sulla mappa [FR-08].<br>Il caso d'uso termina con successo. |
| Extensions              | 2a. OpenStreetMap non è raggiungibile o in timeout.<br>2a.1 Il sistema mostra un messaggio di errore che invita a usare la vista tabellare, il caso d'uso termina con un fallimento.<br>3a. Il database contiene segnalazioni in stato "Resolved" o "Rejected".<br>3a.1 Il sistema le esclude automaticamente dalla visualizzazione sulla mappa [FR-22]. |

| Use Case                |  Visualizzazione segnalazioni su vista tabellare                      |
|:------------------------|:----------------------------|
| ID                      |         UC-12                |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User goal                   |
| Intention in Context    |  Ricercare e filtrare lo storico completo delle segnalazioni tramite un elenco in formato tabellare            |
| Primary actor           |          Cittadino registrato e Cittadino non registrato             |
| Supporting actors       |         -              |
| Stakeholders' interests | **Cittadino non registrato (STK-1)**: vuole consultare lo storico delle segnalazioni applicando filtri per trovare informazioni specifiche sul proprio quartiere senza doversi registrare. **Cittadino registrato (STK-2)**: vuole ricercare segnalazioni per categoria, stato o data per monitorare l'evoluzione dei problemi urbani. **Comune di Torino (STK-9)**: vuole garantire accesso pubblico e trasparente all'archivio completo delle pratiche. |
| Precondition            |           -               |
| Minimum guarantees      |  I dati delle segnalazioni non vengono alterati dall'operazione di consultazione.             |
| Success guarantees      |   L'utente ottiene un elenco coerente con i criteri di ricerca impostati.                        |
| Trigger                 | -                   |
| Main success scenario   |     1. L'utente chiede di consultare la vista tabellare.<br>2. Il sistema mostra la tabella paginata includendo tutte le segnalazioni (anche quelle Resolved/Rejected) in ordine cronologico inverso [FR-11, FR-22].<br>3. L'utente imposta criteri di ricerca (es. intervallo di date, categoria, stato).<br>4. Il sistema filtra i risultati in base ai parametri richiesti e aggiorna la tabella [FR-11].<br>Il caso d'uso termina con successo. |
|Extensions              |        4a. Nessuna segnalazione corrisponde ai criteri di filtro inseriti.<br>4a.1 Il sistema mostra una tabella vuota con il messaggio "Nessun risultato trovato", il caso d'uso termina con successo.


# 3) Traceability Table

| UC ID | REQ ID |
| :---- | :----- |
| UC-XX | FR-XX  |
