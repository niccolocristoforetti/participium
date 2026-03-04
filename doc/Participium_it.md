# Participium

## Scopo e Contesto
**Participium** è un sistema web di partecipazione civica per il Comune di Torino. Il suo obiettivo è offrire un canale strutturato e trasparente attraverso cui i cittadini possono segnalare problemi urbani (ad es. buche, lampioni non funzionanti, rifiuti in strada, barriere architettoniche) e monitorare nel tempo come tali segnalazioni vengono gestite, tramite un’applicazione web responsive.

Il sistema è concepito come una soluzione **open-source** adottabile anche da altre pubbliche amministrazioni. Un esempio reale comparabile è **[IRIS](https://iris.sad.ve.it/)** (Venezia).
![](../data/img/SEP-map.png)

---

## Concetto Chiave
L’oggetto centrale gestito da Participium è la **Segnalazione (Report)**: un problema geolocalizzato inviato da un cittadino registrato, arricchito con informazioni testuali, una categoria e un numero limitato di foto. Le segnalazioni vengono pubblicate su una mappa cittadina e possono essere ricercate, filtrate e tracciate mentre avanzano nella gestione comunale.
![](../data/img/SEP-report.png)

Participium mira a bilanciare:
- **Trasparenza pubblica** (i cittadini possono vedere cosa è stato segnalato e cosa è in gestione),
- **Supporto operativo** (gli uffici comunali possono organizzare e gestire le segnalazioni in ingresso),
- **Comunicazione** (i cittadini ricevono aggiornamenti e possono interagire con gli operatori).

---

## Utenti e Ruoli
Participium supporta diverse tipologie di utenti. I visitatori possono accedere al portale pubblico per consultazione. I cittadini registrati possono inserire segnalazioni, seguirne l’evoluzione e interagire con il Comune. Gli uffici comunali sono responsabili della revisione delle nuove segnalazioni e della gestione di quelle accettate in base alle responsabilità interne (in genere includendo una funzione di verifica iniziale e gli uffici tecnici incaricati degli interventi). Gli amministratori di sistema gestiscono aspetti di configurazione e accedono ad analisi avanzate.

---

## Registrazione e Profilo del Cittadino
Per inserire una segnalazione, l’utente deve creare un account cittadino fornendo informazioni identificative di base (username, nome, cognome) e confermando l’indirizzo email tramite un link di verifica.

I cittadini possono gestire preferenze quali:
- ricevere o meno **notifiche email** oltre alle notifiche in piattaforma,
- opzionalmente una foto profilo.

---

## Inserimento delle Segnalazioni
Una segnalazione viene creata da un cittadino registrato tramite un flusso interattivo centrato sulla mappa cittadina.

### Geolocalizzazione
Il cittadino seleziona una posizione su una mappa di Torino basata su **OpenStreetMap**. La posizione viene salvata come **latitudine/longitudine** ed è il riferimento principale per visualizzare il problema sulla mappa.

### Contenuto e Allegati
Ogni segnalazione include:
- un **titolo** e una **descrizione testuale**,
- una **categoria** selezionata da un insieme predefinito,
- **una o più foto**, fino a un massimo di **3**.

### Opzione di Anonimato Pubblico
Un cittadino può contrassegnare una segnalazione come **anonima** nelle viste pubbliche. In tal caso la segnalazione è pubblicata e tracciabile, ma l’identità del segnalante non è mostrata al pubblico.

---

## Stato della Segnalazione
Ogni segnalazione è associata a un **insieme finito di stati** che riassumono la sua condizione corrente nella gestione comunale:
- **Pending Approval**
- **Assigned**
- **In Progress**
- **Suspended**
- **Rejected**
- **Resolved**

Gli stati servono a comunicare se una segnalazione è ancora in revisione iniziale, è stata inoltrata all’ufficio competente, è in lavorazione, è temporaneamente sospesa, è stata respinta (con motivazione esplicita) oppure è stata chiusa dopo la risoluzione.

---

## Categorie
Le segnalazioni sono classificate per categoria per supportare instradamento, filtri e statistiche. Le categorie definite nella specifica iniziale includono:
- Waterworks – Drinking Water
- Architectural Barriers
- Sewerage
- Public Lighting
- Waste
- Road Signs and Traffic Lights
- Roads and Urban Furniture
- Public Green Areas and Playgrounds
- Other

---

## Consultazione Pubblica: Visualizzazione Mappa e Visualizzazione Tabellare
Participium fornisce un portale pubblico per consultare le segnalazioni pubblicate.

### Visualizzazione Mappa
Le segnalazioni sono mostrate sulla mappa come elementi geolocalizzati. Gli utenti possono esplorare visivamente la città e accedere ai dettagli della segnalazione selezionando una segnalazione dalla mappa.

### Visualizzazione Tabellare
Le segnalazioni sono disponibili anche in una lista strutturata che supporta:
- filtri per categoria e stato,
- filtri per intervallo temporale,
- ordinamento per campi rilevanti (ad es. data).

### Esportazione
La Visualizzazione tabellare consente di esportare i risultati in formato **CSV** per trasparenza, analisi offline o condivisione.

---

## Pagina di Dettaglio della Segnalazione
La pagina di dettaglio presenta il contenuto completo della segnalazione, tipicamente includendo:
- titolo, descrizione, categoria,
- posizione (mostrata sulla mappa),
- foto allegate,
- stato corrente e aggiornamenti disponibili.

La pagina di dettaglio è il punto di riferimento sia per i cittadini sia per il personale comunale per comprendere il problema e seguire gli aggiornamenti.  
I cittadini autenticati possono **seguire** una segnalazione (incluse segnalazioni inserite da altri cittadini) per ricevere aggiornamenti sulla sua evoluzione. Chi segue riceve lo stesso tipo di aggiornamenti (notifiche e, opzionalmente, email) del segnalante originale.

---

## Notifiche e Comunicazione
Un obiettivo chiave di Participium è aumentare la fiducia dei cittadini attraverso una comunicazione chiara.

### Aggiornamenti di Stato
Quando una segnalazione cambia stato durante la gestione comunale, il sistema genera **notifiche in piattaforma** per il cittadino segnalante e per i cittadini che hanno scelto di **seguire** la segnalazione.

### Notifiche Email Opzionali
Ogni notifica in piattaforma può essere inviata anche via **email**, a meno che l’utente non disabiliti questa opzione nel proprio profilo.

### Messaggistica
Participium supporta **messaggistica diretta** tra cittadini e operatori comunali:
- gli operatori possono richiedere chiarimenti o fornire aggiornamenti,
- i cittadini possono rispondere tramite la piattaforma.

La messaggistica è concepita come canale di comunicazione primario.

---

## Statistiche e Reportistica
Participium include funzionalità di analisi sia per la trasparenza sia per il monitoraggio interno.

### Statistiche Pubbliche
Le statistiche pubbliche sono visibili sul sito e accessibili anche agli **utenti non registrati**. Includono:
- numero di segnalazioni per **categoria**,
- trend nel tempo, aggregati per **giorno**, **settimana** o **mese**.

### Statistiche Private
Le statistiche private sono disponibili **solo per gli amministratori**. Oltre alle statistiche pubbliche, includono grafici e tabelle su:
- numero di segnalazioni per **stato**,
- numero di segnalazioni per **tipologia**,
- numero di segnalazioni per **tipologia e stato**,
- numero di segnalazioni per **segnalante**,
- numero di segnalazioni per **segnalante e tipologia**,
- numero di segnalazioni per **segnalante, tipologia e stato**,
- numero di segnalazioni inserite dal **top 1%** dei segnalanti, per tipologia,
- numero di segnalazioni inserite dal **top 5%** dei segnalanti, per tipologia.