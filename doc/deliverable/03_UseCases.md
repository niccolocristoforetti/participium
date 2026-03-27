# 1) Use Case Diagram

Attach your use case diagram as an image under `../data/img/` and link it here:

- `![](../data/img/use-case-diagram.png)`

Also, make sure to include the JSON source file downloaded from the UML Modeler used to draw the diagram in the `../data/` folder.

# 2) Use Case Narratives

Add one narrative for each use case shown in the diagram.
  
| Use Case                | Inserimento Segnalazioni                        |
|:------------------------|:----------------------------|
| ID                      |         UC-06                 |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User Goal                   |
| Intention in Context    |  Creare una segnalazione specificando: posizione sulla mappa, titolo, descrizione, categoria da lista predefinita e fino a 3 foto allegate.                 |
| Primary actor           |          Cittadino registrato                   |
| Supporting actors       |          OpenStreetMap (STK-8)                   |
| Stakeholders' interests |           Cittadino: Inviare la segnalazione in modo rapido e semplice. Comune: Ricevere dati precisi senza saturare l'object storage                  |
| Precondition            |           L'utente è autenticato. L'utente non ha superato il limite massimo di segnalazioni giornaliere (Rate-limiting)                  |
| Minimum guarantees      |              La segnalazione non viene salvata se mancano dati obbligatori (descrizione, categoria, titolo ed almeno una foto).               |
| Success guarantees      |              La segnalazione è salvata con stato "Pending Approval" ed è visibile nel sistema.               |
| Trigger                 |      Il cittadino riscontra un problema urbano e decide di comunicarlo al Comune.                       |
| Main success scenario   |            1. Il sistema mostra la mappa interattiva.<br>2. L'utente seleziona un punto sulla mappa per ottenere le coordinate.<br>3. L'utente sceglie una Categoria. <br>4. L'utente inserisce Titolo e Descrizione.<br>5. L'utente allega fino a 3 foto. Il sistema comprime le immagini lato client se superano i 2 MB.<br>6. L'utente spunta l'opzione "Mantieni anonimo" (opzionale).<br>7. L'utente invia la segnalazione.<br>8. Il sistema crea la segnalazione, le assegna lo stato "Pending Approval" e mostra un messaggio di successo.[FR-05, FR-06] <br>
Il caso d'uso termina con successo.             |
| Extensions              |         3a. L'utente annulla l'inserimento.<br>3a.1 Il sistema non salva la segnalazione, il caso d'uso termina con un fallimento.<br>5a. I dati inseriti non sono validi (es. formato foto errato o campi obbligatori mancanti).<br>5a.1 Il sistema mostra gli errori e il caso d'uso riprende dal punto 3.                    |

| Use Case                |  Consultazione proprie segnalazioni                        |
|:------------------------|:----------------------------|
| ID                      |         UC-07                 |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User Goal                   |
| Intention in Context    |  Visualizzare in dettaglio le segnalazioni inviate personalmente.                 |
| Primary actor           |          Cittadino registrato                   |
| Supporting actors       |          -                  |
| Stakeholders' interests |           Cittadino: Monitorare le pratiche aperte.                 |
| Precondition            |           L'utente è autenticato.                 |
| Minimum guarantees      |              L'utente visualizza le segnalazioni associate al proprio account.               |
| Success guarantees      |              L'utente visualizza l'elenco delle proprie segnalazioni               |
| Trigger                 |        L'utente ha necessità di verificare lo stato di avanzamento delle pratiche che ha aperto.                    |
| Main success scenario   |            1. L'utente chiede di visualizzare le proprie segnalazioni.<br>2. Il sistema interroga il database recuperando tutte le segnalazioni associate all'ID dell'utente loggato.<br>3. Il sistema mostra l'elenco in formato tabellare indicando titolo, data, categoria e stato corrente.<br>Il caso d'uso termina con successo. |
|Extensions              |         2a. L'utente non ha mai effettuato segnalazioni.<br>2a.1 Il sistema mostra un elenco vuoto con un messaggio informativo e il caso d'uso termina con successo.                   |


| Use Case                |  Seguire una segnalazione                       |
|:------------------------|:----------------------------|
| ID                      |         UC-08                 |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User Goal                   |
| Intention in Context    |  Iscriversi ad una segnalazione creata da un altro utente per ricevere aggiornamenti             |
| Primary actor           |          Cittadino registrato                   |
| Supporting actors       |          -                  |
| Stakeholders' interests |           Cittadino: Ricevere aggiornamenti senza dover inserire segnalazioni duplicate; Comune: Ridurre le segnalazioni ridondanti.                 |
| Precondition            |           L'utente è autenticato e visualizza il dettaglio di una segnalazione non creata da lui.                 |
| Minimum guarantees      |   Non vengono create relazioni di follow duplicate.               |
| Success guarantees      |              L'utente risulta follower della segnalazione e riceverà le future notifiche.              |
| Trigger                 |        L'utente individua una pratica di interesse (creata da altri) e decide di volerne monitorare l'evoluzione                     |
| Main success scenario   |            1. L'utente chiede di seguire la segnalazione attualmente visualizzata.<br>2. Il sistema registra la relazione di follow tra l'utente e la segnalazione [FR-09].<br>3. Il sistema aggiorna l'interfaccia confermando che la segnalazione è seguita. <br>Il caso d'uso termina con successo. |
|Extensions              |         2a. L'utente annulla l'operazione.<br>2a.1 Il sistema non registra il follow, il caso d'uso termina con un fallimento.                   |

| Use Case                |  Ricezione notifica                      |
|:------------------------|:----------------------------|
| ID                      |         UC-09                 |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          Subfunction                   |
| Intention in Context    |  Consultare gli avvisi relativi ai cambi di stato delle segnalazioni proprie o seguite             |
| Primary actor           |          Cittadino registrato                   |
| Supporting actors       |          Servizio Notifiche (STK-6)                 |
| Stakeholders' interests |           Cittadino: Essere informato tempestivamente sull'evoluzione dei problemi.                 |
| Precondition            |           L'utente è autenticato. L'operatore comunale cambia lo stato di una segnalazione.               |
| Minimum guarantees      |   L'utente riceve le notifiche ad ogni cambiamento di stato di una segnalazione da lui creata o seguita.               |
| Success guarantees      |              Le notifiche vengono visualizzate e marcate come lette.              |
| Trigger                 |       Il sistema registra un cambio di stato per una segnalazione creata o seguita dall'utente.                    |
| Main success scenario   |     1. Il sistema mostra all'utente l'avviso del cambiamento per la segnalazione da lui effettuata o seguita [FR-13].<br>2. L'utente clicca sulla notifica specifica.<br>3. Il sistema marca la notifica come letta e reindirizza l'utente alla pagina di dettaglio della segnalazione associata.<br>Il caso d'uso termina con successo. |
|Extensions              |         1a. Il Servizio Notifiche non è raggiungibile.<br>1a.1 Il sistema mostra un messaggio di errore temporaneo, il caso d'uso termina con un fallimento.                   |

| Use Case                |  Invio messaggio a operatore                      |
|:------------------------|:----------------------------|
| ID                      |         UC-10                |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          Subfunction                   |
| Intention in Context    |  Inviare una comunicazione diretta all'operatore incaricato per fornire chiarimenti            |
| Primary actor           |          Cittadino registrato                   |
| Supporting actors       |          -               |
| Stakeholders' interests |           Cittadino: Ricevere delucidazioni aggiuntive sulla segnalazioni o per incentivare l'intervento da parte dell'Ufficio Tecnico del Comune; Operatore: Fornisce informazioni sulle segnalazioni, e supporta qualsiasi problema del cittadino                 |
| Precondition            |           L'utente è autenticato.               |
| Minimum guarantees      |   Nessun messaggio vuoto o non valido viene inviato.               |
| Success guarantees      |              Il messaggio arriva all'operatore che può visualizzarlo nella dashboard interna.              |
| Trigger                 |       L'utente ha necessità di fornire dettagli aggiuntivi o richiedere chiarimenti tecnici sulla propria pratica.                  |
| Main success scenario   |     1. L'utente inserisce il testo del messaggio e chiede di inviarlo.<br>2. Il sistema valida il contenuto del messaggio.<br>3. Il sistema salva il messaggio associandolo alla segnalazione e innesca la notifica per l'operatore [FR-15].<br>4. Il sistema aggiorna lo storico chat mostrando il nuovo messaggio inviato.<br>Il caso d'uso termina con successo. |
|Extensions              |         2a. Il testo del messaggio è vuoto.<br>2a.1 Il sistema mostra un errore, il caso d'uso riprende dal punto 1.                   |

| Use Case                |  Visualizzazione segnalazioni su mappa                      |
|:------------------------|:----------------------------|
| ID                      |         UC-11                |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User goal                   |
| Intention in Context    |  Esplorare sulla mappa i problemi urbani segnalati in città            |
| Primary actor           |          Cittadino registrato   e Cittadino non registrato             |
| Supporting actors       |          OpenStreetMap (STK-8)               |
| Stakeholders' interests |           Cittadino registrato e non registrato: Avere una panoramica del territorio con tutti i problemi urbani                 |
| Precondition            |           -               |
| Minimum guarantees      |   Le segnalazioni in stato "Resolved" o "Rejected" non vengono mostrate sulla mappa per evitare disordine visivo.               |
| Success guarantees      |    I marker delle segnalazioni attive vengono renderizzati correttamente sulla mappa                        |
| Trigger                 |      L'utente desidera esplorare visivamente e geograficamente i problemi urbani attivi sul territorio.                    |
| Main success scenario   |     1. L'utente chiede di visualizzare la mappa pubblica.<br>2. Il sistema richiede ed utilizza il servizio di  OpenStreetMap.<br>3. Il sistema interroga il database recuperando esclusivamente le segnalazioni negli stati attivi (Pending, Assigned, In Progress, Suspended) [FR-21].<br>4. Il sistema posiziona i marker sulla mappa[FR-07].<br>Il caso d'uso termina con successo. |
|Extensions              |         2a. OpenStreetMap non è raggiungibile o in timeout.<br>2a.1 Il sistema mostra un messaggio di errore che invita a usare la vista tabellare, il caso d'uso termina con un fallimento.                   |

| Use Case                |  Visualizzazione segnalazioni su vista tabellare                      |
|:------------------------|:----------------------------|
| ID                      |         UC-12                |
| Scope                   |           Piattaforma Participium                   |
| Level                   |          User goal                   |
| Intention in Context    |  Ricercare e filtrare lo storico completo delle segnalazioni tramite un elenco in formato tabellare            |
| Primary actor           |          Cittadino registrato e Cittadino non registrato             |
| Supporting actors       |         -              |
| Stakeholders' interests |           Cittadino registrato e non registrato: Consultare dati applicando filtri specifici per analisi future               |
| Precondition            |           -               |
| Minimum guarantees      |   Vengono illustrate tutte le segnalazioni in base ai filtri applicati              |
| Success guarantees      |   L'utente ottiene un elenco coerente con i criteri di ricerca impostati.                        |
| Trigger                 |       L'utente ha necessità di consultare l'archivio o applicare criteri di ricerca specifici all'elenco delle pratiche.                   |
| Main success scenario   |     1. L'utente chiede di consultare la vista tabellare.<br>2. Il sistema mostra la tabella paginata includendo tutte le segnalazioni (anche quelle Resolved/Rejected) in ordine cronologico inverso [FR-10, FR-21].<br>3. L'utente imposta criteri di ricerca (es. intervallo di date, categoria, stato).<br>4. Il sistema filtra i risultati in base ai parametri richiesti e aggiorna la tabella [FR-10].<br>Il caso d'uso termina con successo. |
|Extensions              |        4a. Nessuna segnalazione corrisponde ai criteri di filtro inseriti.<br>4a.1 Il sistema mostra una tabella vuota con il messaggio "Nessun risultato trovato", il caso d'uso termina con successo.                   |
# 3) Traceability Table

| UC ID | REQ ID |
| :---- | :----- |
| UC-XX | FR-XX  |
