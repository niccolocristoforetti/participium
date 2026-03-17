# 1) Stakeholders

| ID     | Stakeholder name | Description | Role | Main concerns |
|:-------|:-----------------|:------------|:-----|:--------------|
STK-1 | Cittadino non registrato  |	Utente che consulta la piattaforma senza autenticazione. Obiettivo: Informarsi sui problemi urbani. Priorità: Bassa |	Utente | Accesso semplice alle informazioni, visualizzazione della mappa e statistiche |
STK-2 | Cittadino (Registrato) | Utente registrato che può creare e seguire segnalazioni.  Obiettivo: Segnalare/visualizzare problemi urbani. Priorità: Alta |	Utente	| Invio segnalazioni, tracciamento stato, tutela della privacy (anonimato) e messaggistica |
STK-3 |	Operatore comunale	| Gestisce, modera e aggiorna gli stati delle segnalazioni. Obiettivo: Risolvere le pratiche rapidamente. Priorità: Alta	| Utente	| Gestione efficiente delle segalazioni, strumenti per filtrare abusi/spam e foto/dati sensibili |
STK-4	| Admin |	Amministra il sistema e consulta le metriche avanzate. Obiettivo: Garantire la stabilità del sistema e monitorare le metriche. Priorità: Media |	Utente | Controllo accessi, sicurezza dei dati, monitoraggio delle prestazioni |
STK-5	| Servizio di autenticazione |	Servizio di terze parti per l'autenticazione dell'utente. Obiettivo: Fornire login e registrazione sicura. Priorità: Alta |	Sistema esterno	| Sicurezza delle credenziali, disponibilità del servizio, conformità privacy | 
STK-6	| Servizio notifiche |	Sistema per la gestione e l'invio di notifiche in-app. Obiettivo: Recapitare notifiche in-app agli utenti. Priorità: Media |	Sistema esterno	 | Velocità della consegna | 
STK-7 |	Mail server | Server per invio di comunicazioni via email. Obiettivo: Inviare comunicazioni via email in modo sicuro e affidabile. Priorità: Media |	Sistema esterno	 | Sicurezza dei protocolli, garanzia di ricezione | 
STK-8	| OpenStreetMap	|Provider cartografico per la mappa e le coordinate GPS. Obiettivo: Fornire la mappa interattiva e le coordinate GPS. Priorità: Alta| Sistema esterno	| Tempi di risposta delle API, precisione geografica |
STK-9	| Comune di Torino |  Obiettivo: Migliorare la sicurezza urbana. Priorità: Alta | Committente | Costi di gestione |
STK-10 | Ufficio Tecnico del Comune di Torino |  Ricevere segnalazioni (foto, posizione) per poter eseguire i lavori di riparazione sul territorio.Obiettivo: Migliorare la sicurezza urbana. Priorità: Alta | Risolutore | Segnalazioni imprecise o geolocalizzate errata |
STK-11 | Analista | Raccogliere e documentare correttamente i requisiti  Obiettivo: Soddisfare le esigenze del Comune e dei cittadini. Priorità: Media | Project Team | Requisiti ambigui e mancanza di feedback |
STK-12 | Sviluppatore | Seguire le specifiche per creare un software open-source scalabile. Obiettivo: Implementare la piattaforma Participium. Priorità: Alta | Project Team | Specifiche incomplete, complessità di integrazione con sistemi esterni |



---

# 2) Context Diagram

![](/data/img/ContextDiagram.png)

---

# 3) Interfaces

| ID    | Interface | Actor       | Physical interface | Logical interface |
|:------|:----------|:------------|:-------------------|:------------------|
| IF-1 |    Web UI Pubblica      |       Cittadino non registrato (STK-1), Cittadino Registrato (STK-2)      |      Dispositivo utente (Smartphone, PC, Tablet) con connessione ad Internet              |          Applicazione web         |
IF-2 |    Web UI Dashboard Interna     |    Operatore comunale (STK-3), Admin (STK-4)         |       PC con connessione ad Internet             |     Applicazione web (Area riservata)             |
IF-3 |   Portale Amministratore       |    Admin       |    Smartphone/PC con connessione ad Internet               |         Dashboard web di amministrazione           |
IF-4 |    API Autenticazione      |    Servizio di autenticazione (STK-6)         |       Connessione ad Internet             |      API             |
IF-5 |    API Servizio Notifiche       |      Servizio notifiche (STK-7)       |      Connessione ad Internet              |       API            |
IF-6 |     Interfaccia Mail Server       |      Mail server (STK-8)       |     Connessione ad Internet                |    API               |
IF-7 |     API Map Provider server      |      OpenStreetMap (STK-9)       |      Connessione ad Internet              |      API             |


---

# 4) Personas

| ID     | Name | Role | Background / Context | Goals | Constraints | Devices / Usage setting | Accessibility / Additional needs |
|:-------|:-----|:-----|:---------------------|:------|:------------|:------------------------|:---------------------------------|
| PER-XX |      |      |                      |       |             |                         |                                  |

---

# 5) User Stories

| ID    | Persona/Role | User story (As a… I want… so that…) |
|:------|:-------------|:------------------------------------|
| US-XX |              |                                     |

---

# 6) Functional Requirements (FR)

| ID    | Requirement statement (The system shall…) | Priority | User story ID | Notes |
|:------|:------------------------------------------|:---------|:--------------|:------|
| FR-XX |                                           |          |               |       |


---

# 7) Non-Functional Requirements (NFR)

| ID     | Category | Requirement statement | Metric / Target | Verification                           | Priority | Notes |
|:-------|:---------|:----------------------|:----------------|:---------------------------------------|:---------|:------|
| NFR-XX |          |                       |                 |                                        |          |       |
