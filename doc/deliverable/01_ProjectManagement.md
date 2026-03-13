# Product Breakdown Structure (PBS)

| ID | Deliverable | Type  | Notes |
|:---|:------------|:--------------------------------------------------|:------|
| S1 | Applicazione Web (UI + client)           |   Software                                               |  Piattaforma e logica web completa ( UI+client) per la segnalazione civica    |
| S2 | API Gateway / BFF           |   Software  | Modulo di routing (API Gateway o BFF) per gestire le richieste tra frontend e backend, garantendo sicurezza, scalabilità e facilità di manutenzione.
| S3 | Gestione Autenticazione & Servizi utenti / amministratore         |   Software  | Sistema di registrazione, login e autenticazione per gli utenti. Moduli per gestione utenti ed amministratori, ruoli, permessi e profili.
| S4 | Notifications, Messaging & Follow System       |   Software  | Modulo per notifiche in piattaforma, e opzionalmente sulla mail, messaggistica e follow per le segnalazioni e per la comunicazione all'interno della piattaforma per rimanere aggiornati sulle segnalazioni seguite. 
| S5 | Vista mappa cittadina         |   Software  | Modulo software che fornisce una vista mappa interattiva che consenta agli utenti di visualizzare le segnalazioni geolocalizzate.
| S6 | Vista tabellare &  Esportazione dati CSV       |   Software  | Modulo con vista tabellare per la gestione delle segnalazioni e la possibilità di esportare i dati in formato CSV per trasparenza, analisi offline e condivisione.
| S7 | Visualizzazione & Gestione segnalazioni (Report Management) | Software | Motore software per workflow stati segnalazioni, dettaglio segnalazione e moderazione contenuti.
| S8 | Statistiche analitiche pubbliche e private    |   Software | Funzionalità di analisi per utenti (anche non registrati) e amministratori, con visualizzazioni grafiche tabellari per trasparenza e monitoraggio interno  
| I1 | Database     |   Infrastrutture | Istanza di database relazionale per la memorizzazione dei dati della piattaforma
| I2 | Object storage (immagini)     |   Infrastrutture | Spazio di archiviazione per la gestione delle immagini caricate dagli utenti.
| I3 | Mail Server | Infrastrutture | Istanza di mail server per la gestione delle comunicazioni via email.
| I4 | Backup | Infrastrutture | Sistema di backup per garantire la sicurezza e l'integrità dei dati, con procedure di backup regolari e strategie di ripristino in caso di perdita di dati.
| I5 | Pipeline CI/CD & repo (git, ...) | Infrastrutture | Pipeline di integrazione continua e distribuzione continua (CI/CD) attraverso l'uso di strumenti come Git.
| I6 | Metrics, Logging & Monitoring | Infrastrutture | Sistema di monitoraggio e logging per tracciare le prestazioni, identificare problemi e garantire la stabilità della piattaforma.
| I7 | Map Service (OpenStreetMap) | Infrastrutture | Integrazione con un servizio di mappe esterno (OpenStreetMap) per la visualizzazione delle segnalazioni geolocalizzate sulla mappa cittadina.
| D1 | Documento di visione e scopo | Documentazione | Documento che definisce la visione del progetto, gli obiettivi, il contesto. Include una panoramica generale del progetto e la sua importanza per i cittadini.
| D2 | Documento di specifica dei requisiti | Documentazione | Documento che elenca i requisiti funzionali e non funzionali del sistema, basati sulle esigenze degli utenti e degli stakeholder.
| D3 | Documento di progettazione architetturale | Documentazione | Documento che descrive l'architettura del sistema, inclusi i componenti principali, le interazioni tra di essi e le scelte tecnologiche.
| D4 | Documento di specifiche API | Documentazione | Documento che definisce le specifiche e le differenti operazioni delle API (Swagger).
| D5 | Strategie e piano di test | Documentazione | Documento che definisce la strategia di test, i casi di test per garantire la qualità del software.
| D6 | Documento di deployment e gestione operativa | Documentazione | Documento che descrive le procedure di deployment, configurazione e gestione operativa del sistema, inclusi i processi di monitoraggio e manutenzione. 
| D7 | Manuale utente & amministratore| Documentazione | Documento che fornisce istruzioni dettagliate per gli utenti finali e gli amministratori su come utilizzare e gestire la piattaforma.
| D8 | Sicurezza/ Privacy e Legale | Documentazione | Documento che affronta le considerazioni di sicurezza, privacy e legali, inclusi i requisiti di conformità e le misure per proteggere i dati degli utenti.
| D9 | Pianificazione progetto | Documentazione | Documento che descrive la pianificazione del progetto, inclusi i tempi, le risorse e le attività necessarie per completare il progetto con successo.

Considerazioni sulla PBS: La PBS è stata guidata dall'architettura logica descritta nei requisiti di Participium. Il sistema è stato suddiviso in tre macro-aree: moduli Software (per separare nettamente le logiche di frontend, backend, sicurezza, accessi e core workflow), elementi Infrastrutturali (per garantire persistenza, storage multimediale e CI/CD) e artefatti di Documentazione. L'assunzione principale è che il sistema sia sviluppato da zero, ma che utilizzi servizi di terze parti già esistenti per la cartografia (OpenStreetMap - I7) e l'invio email (Server Mail - I3), i quali non vengono costruiti internamente ma integrati.

# Work Breakdown Structure (WBS)

### WBS with traceability to PBS
| ID  | Work package | Traced PBS outputs (IDs) |
|:----|:-------------|:--------------------------|
| 1 | Avvio & Pianificazione | D1,D9
| 2 |  Analisi dei requisiti | D1, D2
| 3 | Architettura UX, API | D3, S2, D4
| 4 | Sviluppo backend | S2, S3, S4, S6, S7, S8, I1, I3, I5, I6
| 4.1 | API + scheletro backend( autenticazione, utenti) |I1, I5, I6, S2, S3
| 4.2 |  Backend(Logica, Workflow, Servizi Avanzati)  | S7, S4, I3, S8, S6
| 5 | Sviluppo frontend | S1, S5, S6, S7, S8, I7
| 6 | Storage services |  I2, I4
| 7 | System Integration & testing funzionale | D5
| 8 | Non functional validation | D5, D8
| 9 | Gestione rilasci | D6, D7 
| 10 | Finalizzazione dei documenti | D3, D4, D6, D7, D8, D9

Considerazioni sulla WBS: La struttura di questa WBS è stata pensata per ottimizzare i tempi di sviluppo, riducendo i colli di bottiglia tra i team (Frontend, Backend e DevOps) e permettendo di lavorare il più possibile in parallelo dopo una fase iniziale di progettazione sequenziale. 
Si è  scelto di dividere il Backend in due: prima si realizza lo "scheletro" delle API (WP 4.1), poi la logica complessa (WP 4.2). Consegnando subito i contratti API al team Frontend, sblocchiamo il loro lavoro permettendo uno sviluppo delle interfacce in totale parallelismo.
Abbiamo diviso l'integrazione in due step: prima verifichiamo che il sistema faccia ciò che deve (WP 7), poi passiamo agli stress test e alla sicurezza (WP 8). Dedicare un pacchetto a parte ai test non-funzionali è fondamentale, trattandosi di una piattaforma civica che gestisce foto e dati sensibili.
La Finalizzazione dei documenti (WP 10) è posizionata alla fine esclusivamente per revisionare gli artefatti, garantendo che rispecchino al 100% il software rilasciato.



# Gantt, dependencies, and critical path

## Activity table
| ID | Activity | Duration | Dependencies | Start | End | Critical | Milestone |
|:---|:---------|:---------|:-------------|:------|:----|:------|:---------|
| T1 | Avvio & Pianificazione | 2 Settimane         |    ---         | S1      | S2    |  SI     |      NO    |
| T2 | Analisi dei requisiti | 3 Settimane         |    T1         | S3      | S5   |  SI     |    SI     |
| T3 | Architettura UX, API | 4 Settimane         |   T2        | S6      | S9    |   SI    |   SI       |
| T4 | API + scheletro backend( autenticazione, utenti)  | 4 Settimane         |     T3     | S10      | S13    |   SI    |    NO      |
| T5 | Backend (Logica, Workflow, Servizi Avanzati)  | 8 Settimane        |   T4       |  S14      | S21   |    NO   |    NO      |
| T6 | Sviluppo frontend   | 10 Settimane        |   T3,T4    | S14      | S23   |   SI    |    NO      |
| T7 | Storage services | 8 Settimane        |   T3     | S10      | S17   |   NO    |   NO       |
| T8 | System Integration & testing funzionale   | 4 Settimane         |   T5,T6,T7     | S24      | S27   |    SI   |    SI     |
| T9 | Non functional validation | 4 Settimane       |  T8     | S28      | S31   |   SI   |    SI      |
| T10 | Gestione rilasci | 3 Settimane         |  T8,T9     | S32      | S34   |   SI    |    SI      |
| T11 | Finalizzazione dei documenti | 2 Settimane         | T10    | S35      | S36   |   SI    |    SI      |

Considerazioni su GANTT: La schedulazione delle attività è stata progettata per rispettare il vincolo temporale di 9 mesi (circa 39 settimane), massimizzando la parallelizzazione laddove l'architettura lo consente. Al termine della progettazione architettonica (T3), il team si divide: la configurazione dello Storage (T7) procede in parallelo allo sviluppo dello scheletro API (T4). A sua volta, il completamento di T4 è il vero "abilitatore" del progetto: consegnando subito i contratti delle API al team, sblocchiamo lo sviluppo in contemporanea della logica Backend avanzata (T5) e del Frontend (T6). Nelle settimane 14-23, il Frontend (T6) risulta l'attività più lunga (10 settimane) a causa della complessità di integrazione della mappa interattiva e della UI. Questo lo pone inevitabilmente sul percorso critico. Il team Backend (T5), richiedendo solo 8 settimane, gode quindi di uno slack di 2 settimane prima dell'inizio della fase di test (T8). Anche l'infrastruttura di Storage (T7) ha un ampio slack di 6 settimane, non impattando minimamente sulla data di consegna.

## Diagramma di Gantt

![Diagramma di Gantt](/data/img/gantt.png)

## Critical path
```
T1 → T2 → T3 → T4 → T6 → T8 → T9 → T10 → T11

```
Considerazioni sul critical path: Il Frontend (T6)  dura 10 settimane (finendo alla settimana 23).
Il Backend (T5) dura 8 settimane (finendo alla 21), quindi ha 2 settimane di slack prima che inizi il testing (T8 alla settimana 24).
Lo Storage (T7) dura 8 settimane ma inizia prima (alla settimana 10), finendo alla 17. Ha 6 settimane di slack prima che serva per il testing.
Durata baseline: 36 settimane — buffer residuo di 3 settimane sul vincolo di 9 mesi (39 settimane).


---

# Risk Management

**Scales and thresholds**
- **Probability (P)**: 1 (rare) … 5 (almost certain)
- **Impact (I)**: 1 (minor) … 5 (critical)
- **Exposure**: `P × I` (range 1–25)

Risk level thresholds (by exposure):
- **Low**: 1–5
- **Medium**: 6–10
- **High**: 11–16
- **Very High**: >16



## Risks table
| ID | Risk | Category | P | I | P×I | Level | Mitigation / Response strategy |
|:---|:-----|:---------|--:|--:|----:|:------|:-------------------------------|
| R1 |   Requisiti non stabili   |     Progetto (Scope)    | 3  |  4 |  12   |    Alto   |      MVP chiaro, Roadmap definita, Congelamento formale dei requisiti        |
| R2 |  Scalabilità (Latenza caricamento mappa/foto)  |     Tecnico / Prestazioni  | 3  |  5 |  15   |    Alto   |    Implementazione del clustering dei marker sulla mappa e stress test prima del rilascio.       |
| R3 |   Caricamento di dati sensibili nelle foto (volti,targhe)   |   Legale / Privacy    | 4  |  4 |  16   |    Molto Alto   |    Inserire un disclaimer obbligatorio prima dell'upload e moderazione manuale da parte degli operatori prima della pubblicazione sulla mappa pubblica.     |
| R4 |  Disservizi di OpenStreetMap  |     Esterno/Tecnico  | 2  |  4 |  8   |    Medio   |    Implementazione di caching lato client/server       |
| R5 |  Vulnerabilità, Data Breach e non conformità GDPR   |     Security/Privacy  | 2  |  5 |  10   |    Medio   |    Test di sicurezza,  cifratura dei dati sensibili nel DB, stesura di un Documento Privacy, log degli accessi    |
| R6 | Abuso del sistema (Spam o segnalazioni false) | Operativo / Sicurezza | 3 | 3 | 9 | Medio | Inserimento di limitazioni (es. max 5 segnalazioni al giorno per utente) e possibilità di ban per gli amministratori |
| R7 | Costi di infrastruttura (Object Storage) superiori alle attese | Economico | 3 | 4 | 12 | Alto | Limiti di budget, compressione delle foto lato client prima dell'upload, test |

Considerazioni sulla Risk Table: L'analisi dei rischi è stata eseguita tenendo a mente il contesto reale di una piattaforma pubblica utilizzata dai cittadini.
Essendo un'app dove chiunque può scattare foto per strada, è quasi certo (Probabilità 4) che vengano inquadrati volti o targhe. Questo espone il Comune a gravi violazioni del GDPR. Per questo motivo R3 è l'unico rischio valutato come "Molto Alto" (16), portandoci ad assumere che sia obbligatoria una moderazione manuale prima di pubblicare le foto sulla mappa.
Se l'app viene molto usata, il caricamento di foto pesanti genererà due problemi: un crollo delle prestazioni della mappa (R2) e un'esplosione dei costi per noleggiare i server di storage (R7). Per risolvere questi rischi si è deciso di implementare la compressione delle foto direttamente lato client prima dell'upload e usare il clustering dei marker per non far "crushare" il browser quando ci sono troppe segnalazioni.
E' molto probabile che una piattaforma comunale aperta a tutti attirerà sicuramente spammer. Da qui la necessità di ridurre l'abuso (R6) tramite rate-limiting (blocchi su chi fa troppe segnalazioni). Inoltre, basando il core dell'app su un servizio esterno (OpenStreetMap), bisogna considerare il rischio di disservizi (R4), introducendo logiche di caching per evitare che l' app smetta di funzionare se il provider delle mappe ha problemi.



