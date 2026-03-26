# 1) Use Case Diagram

Attach your use case diagram as an image under `../data/img/` and link it here:

- `![](../data/img/use-case-diagram.png)`

Also, make sure to include the JSON source file downloaded from the UML Modeler used to draw the diagram in the `../data/` folder.

# 2) Use Case Narratives

Add one narrative for each use case shown in the diagram.
  
### UC-13: Visualizzazione dettaglio segnalazione

| Use Case                | Visualizzazione dettaglio segnalazione |
|:------------------------|:--------------------------------------|
| ID                      | UC-13                                 |
| Scope                   | Piattaforma Participium    |
| Level                   | User goal                             |
| Intention in Context    | L’utente vuole vedere tutte le informazioni su una segnalazione selezionata.
| Primary actor           | Utente (registrato/non registrato)   |
| Supporting actors       | OpenStreetMap |
| Stakeholders' interests | L’utente: (registrato o non) desidera visualizzare i dettagli della segnalazione.<br> Sistema: mostra correttamente i dettagli di una segnalazione |
| Precondition            | la segnalazione deve esistere |
| Minimum guarantees      | - |
| Success guarantees      | Visualizzazione corretta in dettaglio della segnalazione. |
| Trigger                 | Selezione di una segnalazione in elenco o mappa. |
| Main success scenario   | 1. Utente seleziona segnalazione [FR-08].<br> 2. Sistema recupera dati.<br> 3. Sistema mostra dettagli disponibili. |
| Extensions              | 2a. Il sistema ha un errore di caricamento.<br> 2a.1 mostra errore e termina caso d'uso: fallimento.<br> <br>

### UC-14: Esportazione dati in CSV (della vista tabellare)

| Use Case                | Esportazione dati in CSV della vista tabellare |
|:------------------------|:-----------------------------------------------|
| ID                      | UC-14                                          |
| Scope                   | Piattaforma Participium         |
| Level                   | User goal                                      |
| Intention in Context    | L’utente, registrato o non, desidera scaricare localmente i dati della vista tabellare. |
| Primary actor           | Utente (registrato/non registrato)           |
| Supporting actors       | - |
| Stakeholders' interests | Utente: esportazione rapida e completa; Sistema: trasparenza |
| Precondition            | La vista tabellare è popolata con dati delle segnalazioni. |
| Minimum guarantees      | Viene generato un file CSV vuoto solo con header se nessun dato disponibile. |
| Success guarantees      | File CSV scaricabile avente lo stesso contenuto visualizzato. |
| Trigger                 | Utente seleziona opzione per Esportare in CSV. |
| Main success scenario   | 1. Utente richiede esportazione dei dati. [FR-11] <br> 2. Sistema elabora le righe che soddisfano eventuali filtri applicati. <br> 3. Sistema genera CSV. <br> 4. Il file viene scaricato|
| Extensions              | 2a. eccessivo tempo di elaborazione. <br> 2a.1 Presentazione di un  messaggio di errore.

### UC-15: Consultazione statistiche pubbliche

| Use Case                | Consultazione statistiche pubbliche |
|:------------------------|:-----------------------------------|
| ID                      | UC-15                              |
| Scope                   | Piattaforma Participium     |
| Level                   | User goal                          |
| Intention in Context    | L’utente, registrato o no, vuole accedere a statistiche generali sulle segnalazioni. |
| Primary actor           | Utente (registrato/non registrato) |
| Supporting actors       | - |
| Stakeholders' interests | L’utente: trasparenza<br> Analista: fare analisi per gli obiettivi del Comune <br> Comune: accountability e insight. |
| Precondition            | Esistono dati sufficienti per la creazione di statistiche rilevanti. |
| Minimum guarantees      | Mostra un messaggio di “nessun dato” se non disponibili. |
| Success guarantees      | Fornisce statistiche aggiornate ed aggregate. |
| Trigger                 | Accesso alla sezione “Statistiche pubbliche”. |
| Main success scenario   | 1. Utente entra nella sezione.<br> 2. Sistema calcola metriche.<br> 3. Sistema mostra grafici/tabelle.[FR-13] <br> |
| Extensions              | 2a. Errore calcolo.<br> 2a.1 messaggio, eventuale retry.<br> <br> 3a. Filtri errati(no dati sufficienti)<br> 3a.1 Reset filtri.

### UC-16: Accettazione/rifiuto segnalazione (con motivazione)

| Use Case                | Accettazione/rifiuto segnalazione |
|:------------------------|:---------------------------------|
| ID                      | UC-16                            |
| Scope                   | Piattaforma Participium  |
| Level                   | User goal                |
| Intention in Context    | Operatore comunale valuta e definisce se una segnalazione è valida o non valida, allegando motivazioni. |
| Primary actor           | Operatore comunale              |
| Supporting actors       | Server mail |
| Stakeholders' interests | Comune: correttezza processuale, segnalazioni corrette <br> Utenti: attendibilità delle segnalazioni.<br> Amministratore: supervisione, anche degli account. |
| Precondition            | Operatore autenticato e segnalazione in stato “nuova”. |
| Minimum guarantees      | accettazione o rifiuto con motivazione, anche se la segnalazione viene rifiutata  viene loggato il tutto. |
| Success guarantees      | Stato aggiornato a “accettata” o “rifiutata” con motivazione salvata. |
| Trigger                 | Operatore seleziona azione accetta/rifiuta + motivazione. |
| Main success scenario   | 1. Operatore seleziona segnalazione.<br> 2. Indica decisione e motivazione. [FR-18]<br> 3. Sistema salva aggiornamento.<br> 4. Sistema notifica il segnalatore ed i follower (della segnalazione)del cambio di stato.[FR-14, FR-18] |
| Extensions              | 2a. Motivazione mancante<br>2a.1 Richiesta motivazione obbligatoria.<br><br> 2b Stato mancante.<br>2b.1 Selezione dello stato obbligatoria.<br>

# 3) Traceability Table

| UC ID | REQ ID |
| :---- | :----- |
| UC-XX | FR-XX  |
