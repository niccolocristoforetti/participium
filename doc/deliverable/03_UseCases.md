# 1) Use Case Diagram

Attach your use case diagram as an image under `../data/img/` and link it here:

- `![](../data/img/use-case-diagram.png)`

Also, make sure to include the JSON source file downloaded from the UML Modeler used to draw the diagram in the `../data/` folder.

# 2) Use Case Narratives

Add one narrative for each use case shown in the diagram.
| Use Case                |           Registrazione                 |
|:------------------------|:----------------------------|
| ID                      | UC-01                            |
| Scope                   | Piattaforma Participium                            |
| Level                   | User goal                            |
| Intention in Context    | Creare un nuovo account per partecipare attivamente alla piattaforma                            |
| Primary actor           | Cittadino non registrato                            |
| Supporting actors       | Servizio di autenticazione (STK-5), Mail server (STK-7) |
| Stakeholders' interests | **Cittadino non registrato (STK-1)**: Vuole creare un account per poter inserire segnalazioni. **Comune(STK-9)**: Avere la garanzia che gli utenti registrati siano reali e verificati, riducendo i rischi di sicurezza (GDPR) non conservando direttamente le credenziali di accesso.|
| Precondition            | L'utente possiede un indirizzo email valido. |
| Minimum guarantees      |Nessun dato personale viene persistito in caso di registrazione non completata. Le credenziali (password) non vengono mai salvate nei database di Participium. |
| Success guarantees      | L'utente dispone di un account attivo e verificato sulla piattaforma. L'utente può effettuare il login. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente chiede di potersi registrare.<br>2. Il sistema reindirizza l'utente al Servizio di Autenticazione esterno [FR-01].<br>3. L'utente inserisce username, nome, cognome, indirizzo email e password.<br>4. L'utente conferma e invia il modulo di registrazione.<br>5. Il sistema crea l'account in stato "non verificato" e invia un'email con link di verifica [FR-01].<br>6. L'utente clicca sul link di verifica ricevuto via email.<br>7. Il sistema attiva l'account [FR-01].<br>8. Il sistema propone al cittadino di completare il profilo: caricare opzionalmente una foto profilo [FR-05] e impostare le preferenze di notifica email [FR-04].<br>9. Il cittadino configura le preferenze desiderate.<br>10. Il sistema salva le impostazioni selezionate [FR-04] [FR-05].<br>11. L'utente viene reindirizzato alla piattaforma come utente autenticato.<br>Il caso d'uso termina con successo |
| Extensions              | 4a. L'utente annulla la registrazione.<br>4a.1 Il sistema non crea l'account, il caso d'uso termina con un fallimento.<br>5a. I dati inseriti non sono validi o sono incompleti.<br>5a.1 Il sistema mostra gli errori e il caso d'uso riprende dal punto 2.<br>9a. Il cittadino salta la configurazione del profilo.<br>9a.1 Il sistema mantiene le impostazioni predefinite e il caso d'uso riprende dal punto 10. |

| Use Case                |           Recupero password                  |
|:------------------------|:----------------------------|
| ID                      | UC-02                          |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Ripristinare l'accesso al proprio account in caso di smarrimento della password           |
| Primary actor           | Cittadino registrato (non loggato) |
| Supporting actors       | Servizio di autenticazione (STK-5), Mail server (STK-7) |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole recuperare l'accesso al proprio account. |
| Precondition            | L'utente possiede un account sulla piattaforma. |
| Minimum guarantees      | Le credenziali precedenti rimangono valide fino al completamento del reset. |
| Success guarantees      | L'utente ha impostato una nuova password e può effettuare il login. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente accede alla pagina di recupero password.<br>2. Il sistema reindirizza la richiesta al Servizio di Autenticazione esterno.<br>3. L'utente inserisce l'indirizzo email associato al proprio account.<br>4. L'utente conferma e invia la richiesta.<br>5. Il Servizio di Autenticazione esterno verifica l'email e genera un link di reset [FR-02].<br>6. Il Servizio di Autenticazione esterno invia un'email con il link di reset all'indirizzo fornito [FR-02].<br>7. L'utente accede al link di reset ricevuto via email.<br>8. L'utente inserisce e conferma la nuova password.<br>9. Il sistema aggiorna le credenziali [FR-02].<br>10. L'utente viene reindirizzato alla pagina di login. |
| Extensions              | 4a. L'utente annulla il recupero.<br>4a.1 Il sistema non invia nessuna email, il caso d'uso termina con un fallimento.<br>8a. Le password inserite non coincidono o non rispettano i requisiti di sicurezza.<br>8a.1 Il sistema mostra gli errori e il caso d'uso riprende dal punto 8. |



| Use Case                |          Login                   |
|:------------------------|:----------------------------|
| ID                      | UC-03                          |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Autenticarsi in modo sicuro per accedere a diverse funzionalità della piattaforma                       |
| Primary actor           | Utente registrato (Cittadino, Operatore comunale, Admin) |
| Supporting actors       | Servizio di autenticazione (STK-5) |
| Stakeholders' interests | **Cittadino (STK-2)**: vuole accedere alla propria area riservata per gestire le segnalazioni. **Operatore comunale (STK-3)**: vuole accedere alla dashboard interna per gestire le pratiche. **Admin(STK-4)**:vuole accedere alla dashboard privata per amministrare il sistema e consulta le metriche avanzate |
| Precondition            | L'utente possiede un account attivo e verificato sulla piattaforma. |
| Minimum guarantees      | -|
| Success guarantees      | L'utente dispone di una sessione autenticata attiva con i permessi corrispondenti al proprio ruolo. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente accede alla pagina di login.<br>2. Il sistema reindirizza l'utente alla schermata del Servizio di Autenticazione esterno. <br>3. L'utente inserisce username e password.<br>4. L'utente conferma e invia il modulo di login.<br>5. Il sistema verifica le credenziali tramite il servizio di autenticazione [FR-03].<br>6. Il sistema crea una sessione autenticata [FR-03].<br>7. L'utente viene reindirizzato all'area riservata corrispondente al proprio ruolo. |
| Extensions              | 4a. L'utente annulla il login.<br>4a.1 Il sistema non crea nessuna sessione, il caso d'uso termina con un fallimento.<br>5a. Le credenziali inserite non sono corrette.<br>5a.1 Il sistema mostra un messaggio di errore generico e il caso d'uso riprende dal punto 3. |

| Use Case                |          Logout                   |
|:------------------------|:----------------------------|
| ID                      | UC-04                          |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Logout                      |
| Primary actor           | Utente registrato (Cittadino, Operatore comunale, Admin) |
| Supporting actors       | Servizio di autenticazione (STK-5) |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole terminare la sessione in modo sicuro per tutelare i propri dati. **Operatore comunale (STK-3)**: vuole disconnettersi al termine del turno di lavoro. **Admin(STK-4)**: vuole disconnettersi dalla dashboard privata dopo aver svolto i suoi compiti|
| Precondition            | L'utente è autenticato sulla piattaforma. |
| Minimum guarantees      | - |
| Success guarantees      | La sessione dell'utente è terminata e nessun dato personale rimane accessibile senza nuova autenticazione. |
| Trigger                 | - |
| Main success scenario   | 1. L'utente richiede il logout.<br>2. Il sistema invalida la sessione autenticata [FR-03].<br>3. Il sistema richiede al Servizio di Autenticazione esterno di invalidare la sessione globale.<br>4. L'utente viene reindirizzato alla pagina pubblica della piattaforma. |
| Extensions              | - |

| Use Case                |            Aggiornamento profilo                 |
|:------------------------|:----------------------------|
| ID                      | UC-05                          |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Modificare le proprie informazioni opzionali e le impostazioni di ricezione email.       |
| Primary actor           | Cittadino registrato |
| Supporting actors       | -                           |
| Stakeholders' interests | **Cittadino registrato (STK-2)**: vuole personalizzare il proprio profilo e gestire le preferenze di notifica. |
| Precondition            | L'utente è autenticato sulla piattaforma. |
| Minimum guarantees      | Le modifiche non confermate non vengono persistite. |
| Success guarantees      | Le nuove impostazioni del profilo sono attive. |
| Trigger                 | - |
| Main success scenario   | 1. Il cittadino accede alla sezione del proprio profilo. Il sistema mostra le impostazioni correnti.<br>2. Il cittadino apporta le modifiche desiderate: aggiorna le preferenze di notifica email [FR-04] e/o carica una nuova foto profilo [FR-05].<br>3. Il cittadino conferma e salva le modifiche.<br>4. Il sistema aggiorna il profilo con le nuove impostazioni [FR-04] [FR-05].<br>5. Il sistema mostra la conferma di avvenuto aggiornamento. |
| Extensions              | 2a. L'utente tenta di caricare una foto di formato o dimensione non supportata.<br>2a.1 Il sistema mostra un errore e richiede un file valido, il caso d'uso riprende dal punto 2.<br>3a. Il cittadino annulla le modifiche.<br>3a.1 Il sistema non persiste nessuna modifica, il caso d'uso termina.|

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

| Use Case                | Visualizzazione dettaglio segnalazione |
|:------------------------|:--------------------------------------|
| ID                      | UC-13                                 |
| Scope                   | Piattaforma Participium    |
| Level                   | User goal                             |
| Intention in Context    | Cittadino vuole vedere tutte le informazioni su una segnalazione selezionata.
| Primary actor           | Cittadino (registrato/non registrato)   |
| Supporting actors       | OpenStreetMap |
| Stakeholders' interests | **Cittadino registrato/ non registrato [STK-1, STK-2]**: (registrato o non) desidera visualizzare i dettagli della segnalazione.<br> **Comune di Torino [STK-9]**: mostrare correttamente i dettagli di una segnalazione |
| Precondition            | La segnalazione deve esistere |
| Minimum guarantees      | - |
| Success guarantees      | Visualizzazione corretta in dettaglio della segnalazione. |
| Trigger                 | - |
| Main success scenario   | 1. Cittadino seleziona segnalazione dalla mappa o dalla vista tabellare[FR-09].<br> 2. Sistema recupera dati.<br> 3. Sistema mostra dettagli disponibili.<br> Il caso d'uso termina con successo.|
| Extensions              | 2a. Il sistema ha un errore di caricamento.<br> 2a.1 mostra errore e termina caso d'uso.<br> <br>


| Use Case                | Esportazione dati in CSV della vista tabellare |
|:------------------------|:-----------------------------------------------|
| ID                      | UC-14                                          |
| Scope                   | Piattaforma Participium         |
| Level                   | User goal                                      |
| Intention in Context    | Cittadino, registrato o non, desidera scaricare localmente i dati della vista tabellare. |
| Primary actor           | Cittadino (registrato/non registrato)           |
| Supporting actors       | - |
| Stakeholders' interests | **Cittadino registrato/non registrato[STK-1, STK-2]**: esportazione rapida e completa;  |
| Precondition            | - |
| Minimum guarantees      | Viene generato un file CSV vuoto solo con header se nessun dato disponibile. |
| Success guarantees      | File CSV scaricabile avente lo stesso contenuto visualizzato della vista tabellare. |
| Trigger                 | - |
| Main success scenario   | 1. Cittadino richiede esportazione dei dati. [FR-12] <br> 2. Sistema elabora le righe che soddisfano eventuali filtri applicati. <br> 3. Sistema genera CSV. <br> 4. Il file viene scaricato<br> Il caso d'uso termina con successo.|
| Extensions              | 2a. eccessivo tempo di elaborazione. <br> 2a.1 Presentazione di un  messaggio di errore.


| Use Case                | Consultazione statistiche pubbliche |
|:------------------------|:-----------------------------------|
| ID                      | UC-15                              |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                          |
| Intention in Context    | Cittadino, registrato o non, vuole accedere a statistiche generali sulle segnalazioni. |
| Primary actor           | Cittadino (registrato/non registrato) |
| Supporting actors       | - |
| Stakeholders' interests | **Cittadino[STK-1, STK-2]**: trasparenza<br> **Comune[STK-9]**: accountability e insight. |
| Precondition            | - |
| Minimum guarantees      | Mostra un messaggio di “nessun dato” se non disponibili. |
| Success guarantees      | Fornisce statistiche aggiornate ed aggregate. |
| Trigger                 | - |
| Main success scenario   | 1. Cittadino entra nella sezione specifica.<br> 2. Sistema calcola metriche.<br> 3. Sistema mostra grafici/tabelle.[FR-13]<br> Il caso d'uso termina con successo. |
| Extensions              | 2a. Errore calcolo.<br> 2a.1 messaggio, eventuale retry.<br> 


| Use Case                | Accettazione/rifiuto segnalazione |
|:------------------------|:---------------------------------|
| ID                      | UC-16                            |
| Scope                   | Piattaforma Participium  |
| Level                   | User goal                |
| Intention in Context    | Operatore comunale valuta e definisce se una segnalazione è valida o non valida, allegando motivazioni. |
| Primary actor           | Operatore comunale              |
| Supporting actors       | Server mail |
| Stakeholders' interests | **Operatore Comunale[STK-3]**: correttezza processuale, segnalazioni corrette <br> **Cittadino registrato[STK-2]**: attendibilità delle segnalazioni.<br>  |
| Precondition            | Operatore autenticato. |
| Minimum guarantees      | Accettazione o rifiuto con motivazione, anche se la segnalazione viene rifiutata  viene loggato il tutto. |
| Success guarantees      | Stato aggiornato a “Resolved” o "Rejected" con motivazione salvata. |
| Trigger                 | Il cittadino registrato inserisce una nuova segnalazione |
| Main success scenario   | 1. Operatore seleziona segnalazione.<br> 2. Indica decisione e motivazione. [FR-19]<br> 3. Sistema salva aggiornamento.<br> 4. Sistema notifica il segnalatore ed i follower (della segnalazione)del cambio di stato.[FR-15, FR-19] <br> Il caso d'uso termina con successo.|
| Extensions              | 2a. Motivazione mancante<br>2a.1 Richiesta motivazione obbligatoria.<br>


| Use Case                | Aggiornamento stato e note segnalazione |
|:------------------------|:--------------------------------------|
| ID                      | UC-17                                 |
| Scope                   | Piattaforma Participium    |
| Level                   | User goal                             |
| Intention in Context    | Operatore deve aggiornare lo stato e le note delle segnalazioni. |
| Primary actor           | Operatore comunale                   |
| Supporting actors       | - |
| Stakeholders' interests | **Operatore Comunale[STK-3]**: gestione trasparente<br> **Cittadino registrato /non registrato[STK-1, STK-2]**: trasparenza stato<br> **Ufficio Tecnico del Comune di Torino [STK-10]**: avere informazioni necessarie per effettuare gli interventi. |
| Precondition            | Operatore comunale autenticato e segnalazione esistente. |
| Minimum guarantees      | Lo stato o le note sono persistenti a prescindere dall'aggiornamento. |
| Success guarantees      | Si ha aggiornamento dello stato della segnalazione e/o l'aggiunta di una nota. Quando la segnalazione cambia stato si invierà una notifica. |
| Trigger                 | - |
| Main success scenario   | 1. Seleziona segnalazione.<br> 2. Modifica stato e/o note. [FR-18, FR-19]<br> 3. Invia notifica di cambio stato e/o aggiunta nota. [FR-14, FR-15]<br> Il caso d'uso termina con successo. |
| Extensions              |  2a Errore, non viene effettuata la modifica<br>


| Use Case                | Moderazione contenuti |
|:------------------------|:----------------------|
| ID                      | UC-18                |
| Scope                   | Piattaforma Participium |
| Level                   | User goal            |
| Intention in Context    | Operatore identifica contenuti non conformi (testo/foto) e avvia una segnalazione all’amministratore. |
| Primary actor           | Operatore comunale  |
| Supporting actors       | Admin |
| Stakeholders' interests | **Cittadino registrato / non registrato [STK-1, STK-2]**: attendibilità segnalazioni <br> **Admin [STK-4]**: monitoraggio. <br> **Operatore Comunale [STK-3]**: garantire un sistema affidabile.|
| Precondition            | Operatore autenticato, contenuto segnalato identificato. |
| Minimum guarantees      | -|
| Success guarantees      | La segnalazione viene inviata all'admin |
| Trigger                 | Operatore rifiuta una segnalazione |
| Main success scenario   | 1. Fornisce motivo e dettagli per rimozione.[FR-24]<br> 2. Il sistema crea il messaggio di segnalazione del cittadino.<br> Il caso d'uso termina con successo.|
| Extensions              | 1a. Dati insufficienti<br> 1a.1 Richieste ulteriori varifiche.


| Use Case                |  Risposta a messaggi cittadini                      |
|:------------------------|:----------------------------|
| ID                      | UC-19                        |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Fornire chiarimenti o aggiornamenti diretti al cittadino in risposta a una sua richiesta |
| Primary actor           | Operatore comunale |
| Supporting actors       | Servizio notifiche (STK-6), Mail server (STK-7) |
| Stakeholders' interests | **Operatore comunale (STK-3)**: vuole comunicare in modo rapido e tracciato con il segnalante per risolvere dubbi operativi. **Cittadino registrato (STK-2)**: vuole ricevere risposte chiare senza dover telefonare agli uffici. |
| Precondition            | L'operatore è autenticato e visualizza il dettaglio di una segnalazione con messaggi inviati dai cittadini. |
| Minimum guarantees      | I messaggi inviati vengono storicizzati e associati permanentemente alla segnalazione. |
| Success guarantees      | Il messaggio è recapitato al cittadino e la cronologia della conversazione è aggiornata. |
| Trigger                 | Ricezione di un messaggio da parte di un cittadino. |
| Main success scenario   | 1. L'operatore accede alla sezione messaggistica della segnalazione specifica.<br>2. L'operatore inserisce il testo della risposta.<br>3. L'operatore conferma l'invio.<br>4. Il sistema valida il contenuto e salva il messaggio [FR-16].<br>5. Il sistema invia una notifica push al cittadino segnalante tramite il servizio notifiche [FR-14] e, se abilitata, una notifica email tramite mail server [FR-15].<br>6. Il sistema aggiorna l'interfaccia della chat mostrando il nuovo messaggio. Il caso d'uso termina con successo. |
| Extensions              | - |


| Use Case                |  Visualizzazione segnalazioni in dashboard (con filtro) |
|:------------------------|:----------------------------|
| ID                      | UC-20                        |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Monitorare e gestire il carico di lavoro tramite una vista d'insieme delle segnalazioni attive |
| Primary actor           | Operatore comunale |
| Supporting actors       | -                           |
| Stakeholders' interests | **Operatore comunale (STK-3)**: vuole una lista chiara dei ticket prioritari da gestire per organizzare gli interventi. **Comune di Torino (STK-9)**: vuole efficienza nella gestione dei tempi di risposta ai cittadini. |
| Precondition            | L'operatore è autenticato nell'area gestionale. |
| Minimum guarantees      | -                           |
| Success guarantees      | L'operatore visualizza i dati aggiornati filtrati secondo i propri criteri di competenza. |
| Trigger                 | -                           |
| Main success scenario   | 1. L'operatore accede alla dashboard principale del sistema.<br>2. Il sistema mostra la tabella completa di tutte le segnalazioni attive [FR-11].<br>3. L'operatore imposta i filtri desiderati (es. "Solo segnalazioni in stato Pending Approval", "Categoria: Buche", "Zona: Circoscrizione 7") [FR-17].<br>4. Il sistema interroga il database e aggiorna la vista mostrando solo i risultati pertinenti.<br>Il caso d'uso termina con successo. |
| Extensions              | 4a. Nessuna segnalazione corrisponde ai filtri impostati.<br>4a.1 Il sistema mostra un messaggio "Nessun risultato trovato", il caso d'uso termina con successo. |


| Use Case                |  Gestione account operatori comunali                |
|:------------------------|:----------------------------|
| ID                      | UC-21                        |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Configurare e gestire gli accessi per il personale degli uffici tecnici comunali |
| Primary actor           | Amministratore |
| Supporting actors       | Servizio di autenticazione (STK-5), Mail server (STK-7) |
| Stakeholders' interests | **Admin (STK-4)**: vuole gestire i permessi del personale comunale in modo centralizzato e sicuro. **Comune di Torino (STK-9)**: vuole che solo personale autorizzato acceda ai dati sensibili delle segnalazioni. |
| Precondition            | L'Admin è autenticato nella dashboard amministrativa privata. |
| Minimum guarantees      | L'account non viene creato se l'email istituzionale non è valida o già presente. |
| Success guarantees      | Un nuovo profilo operatore è attivo nel sistema con le credenziali inviate via email. |
| Trigger                 | Necessità di autorizzare un nuovo dipendente all'uso della piattaforma. |
| Main success scenario   | 1. L'Admin accede alla sezione "Gestione Personale Staff".<br>2. L'Admin inserisce i dati identificativi dell'operatore (nome, email istituzionale, ufficio di competenza).<br>3. L'Admin conferma la creazione dell'account.<br>4. Il sistema invia la richiesta di creazione utenza al Servizio di Autenticazione esterno [FR-20].<br>5. Il sistema genera e invia un'email automatica all'operatore con le istruzioni per il primo accesso.<br>6. Il sistema aggiunge il nuovo operatore alla lista degli utenti attivi. Il caso d'uso termina con successo. |
| Extensions              | 3a. L'Admin decide di revocare l'accesso a un operatore esistente.<br>3a.1 L'Admin seleziona "Disabilita Account", il sistema invalida la sessione e impedisce nuovi login all'operatore [FR-20]. |


| Use Case                |  Gestione utenti abusivi (ban)                      |
|:------------------------|:----------------------------|
| ID                      | UC-22                        |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Sospendere l'accesso a utenti che caricano spam o contenuti inappropriati |
| Primary actor           | Amministratore  |
| Supporting actors       | -                           |
| Stakeholders' interests | **Admin (STK-4)**: vuole proteggere l'integrità dei dati e la reputazione della piattaforma. **Cittadini (STK-2)**: vogliono un ambiente civile e privo di segnalazioni false o offensive. |
| Precondition            | L'utente in questione è stato segnalato da un operatore per violazione dei termini (UC-18). |
| Minimum guarantees      | Tutte le segnalazioni pendenti dell'utente bannato vengono rimosse dalla vista pubblica. |
| Success guarantees      | L'utente non può più autenticarsi o interagire con la piattaforma. |
| Trigger                 | L'Admin riceve la segnalazione di un utente da parte effettuata da un operatore comunale. |
| Main success scenario   | 1. L'Admin accede alla lista degli utenti segnalati per abusi.<br>2. L'Admin revisiona le segnalazioni e le prove caricate (es. foto inappropriate).<br>3. L'Admin seleziona l'opzione "Ban Utente".<br>4. Il sistema comunica al Servizio di Autenticazione di revocare i permessi all'utente [FR-23].<br>5. Il sistema disabilita la sessione attiva dell'utente e nasconde le sue segnalazioni correnti dalla vista pubblica [FR-23].<br>6. Il sistema registra l'azione nel log di moderazione. Il caso d'uso termina con successo. |
| Extensions              | 3a. L'Admin ritiene la violazione lieve.<br>3a.1 L'Admin invia solo un ammonimento formale tramite email e non procede al ban. |


| Use Case                |  Consultazione statistiche private                  |
|:------------------------|:----------------------------|
| ID                      | UC-23                        |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                   |
| Intention in Context    | Analizzare i dati aggregati per monitorare l'andamento del servizio e le performance degli uffici |
| Primary actor           | Amministratore |
| Supporting actors       | -                           |
| Stakeholders' interests | **Admin (STK-4)**: vuole misurare l'efficienza degli uffici tecnici e il volume di segnalazioni per quartiere. **Comune di Torino (STK-9)**: vuole dati oggettivi per pianificare interventi di manutenzione stradale a lungo termine. |
| Precondition            | L'Admin è autenticato.      |
| Minimum guarantees      | I dati sono presentati in forma aggregata garantendo la privacy dei singoli segnalanti. |
| Success guarantees      | L'Admin visualizza dashboard interattive con trend temporali e performance. |
| Trigger                 | -                           |
| Main success scenario   | 1. L'Admin accede alla sezione "Analytics e Reporting" della piattaforma.<br>2. Il sistema genera automaticamente grafici su: volumi per categoria, tempi medi di risoluzione e performance degli operatori [FR-21].<br>3. L'Admin applica filtri temporali (es. "Ultimo semestre") o geografici.<br>4. Il sistema aggiorna i report in tempo reale.<br>5. L'Admin esporta opzionalmente i dati in formato CSV per uso istituzionale [FR-12]. Il caso d'uso termina con successo. |
| Extensions              | -                           |




# 3) Traceability Table

| UC ID | REQ ID |
| :---- | :----- |
| UC-XX | FR-XX  |
