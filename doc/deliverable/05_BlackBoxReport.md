## 1 `participium.services.auth_service.AuthService.authenticate`

Suggested test file: `test_authenticate.py`

Prototype: `authenticate(identifier: str, password: str) -> User`

**Requirements**:

Il sistema deve autenticare un utente tramite username o email e password in chiaro.

L'identificatore deve essere normalizzato tramite `strip()` prima del confronto; il confronto per email deve essere case-insensitive.

Se l'identificatore è vuoto (dopo normalizzazione), il sistema deve sollevare `AuthenticationError`.

Se nessun utente corrisponde all'identificatore fornito, il sistema deve sollevare `AuthenticationError`.

Se la password è vuota o non corrisponde all'hash memorizzato dell'utente trovato, il sistema deve sollevare `AuthenticationError`.

Se l'utente corrispondente è inattivo (`is_active == False`), il sistema deve sollevare `AuthenticationError`.

Se l'email dell'utente non è verificata (`is_email_verified == False`), il sistema deve sollevare `AuthenticationError`.

Altrimenti il sistema deve restituire l'utente autenticato.

**Criterion**:
- identifier

**Predicates**:
- identifier è vuoto (dopo strip) → non valido (AuthenticationError)
- identifier non vuoto, nessun utente corrispondente → non valido (AuthenticationError)
- identifier non vuoto, corrisponde a un utente per username → valido (continua)
- identifier non vuoto, corrisponde a un utente per email → valido (continua)
- identifier è email con spazi iniziali/finali → normalizzato via strip, corrisponde a un utente per email → valido (continua)
- identifier è email con caratteri upper case → normalizzato via lowercase, corrisponde a un utente per email → valido (continua)
- identifier è username con spazi iniziali/finali → normalizzato via strip, corrisponde a un utente per username → valido (continua)

**Criterion**:
- password (quando identifier corrisponde a un utente)

**Predicates**:
- password è vuota → non valida (AuthenticationError)
- password non corrisponde all'hash memorizzato → non valida (AuthenticationError)
- password corrisponde all'hash memorizzato → valida (continua)

**Criterion**:
- stato utente (quando identifier e password sono validi)

**Predicates**:
- utente inattivo (`is_active == False`) → non valido (AuthenticationError)
- email non verificata (`is_email_verified == False`) → non valido (AuthenticationError)
- utente attivo ed email verificata → valido (User)

**Equivalence Classes**

Per identifier:

- EC1: identifier vuoto
- EC2: identifier non vuoto, nessun utente con username corrispondente
- EC3: identifier non vuoto, nessun utente con email corrispondente
- EC4: identifier non vuoto, corrisponde a un utente per username
- EC5: identifier non vuoto, corrisponde a un utente per email
- EC6: identifier è email con spazi iniziali/finali, corrisponde a un utente per email dopo strip
- EC7: identifier è email con caratteri upper case, corrisponde a un utente per email dopo lowercase
- EC8: identifier è username con spazi iniziali/finali, corrisponde a un utente per username dopo strip

Per password (quando EC4 o EC5):

- EC9: password vuota
- EC10: password non vuota, non corrisponde all'hash memorizzato
- EC11: password non vuota, corrisponde all'hash memorizzato

Per stato utente (quando EC4/EC5 e EC11):

- EC12: utente inattivo
- EC13: utente attivo, email non verificata
- EC14: utente attivo, email verificata

**Combinations of equivalence classes**

    EC4 × EC11 × EC14
    EC5 × EC11 × EC14
    EC2
    EC3
    EC4 × EC10
    EC5 × EC10
    EC4 × EC11 × EC12
    EC5 × EC11 × EC12
    EC5 × EC11 × EC13
    EC4 × EC11 × EC13
    EC1
    EC4 × EC9
    EC5 × EC9
    EC1 × EC9
    EC6 × EC11 × EC14
    EC7 × EC11 × EC14
    EC8 × EC11 × EC14

| TC-ID | identifier | password | Expected | Fixture | EC covered |
| :---- | :--------- | :------- | :------- | :------ | :--------- |
| AUTH1 | `"mario.rossi"` (username valido) | `"correct_password"` | restituisce `User` (associato ad username: `"mario.rossi"`) | utente esistente e attivo, password hash corrispondente | EC4, EC11, EC14 |
| AUTH2 | `"mario.rossi@example.com"` (email valida) | `"correct_password"` | restituisce `User` (associato ad email: `"mario.rossi@example.com"`) | utente esistente e attivo, email verificata, password hash corrispondente | EC5, EC11, EC14 |
| AUTH3 | `"unknown_user"` (non esistente) | `"any_password"` | `AuthenticationError` | Nessun utente nel Database con username associata: `"unknown_user"` | EC2 |
| AUTH4 | `"unknown_user@example.com"` (non esistente) | `"any_password"` | `AuthenticationError` | Nessun utente nel Database con email associata: `"unknown_user"` | EC3 |
| AUTH5 | `"mario.rossi"` (esistente) | `"wrong_password"` | `AuthenticationError` | utente esistente, password hash non corrispondente | EC4, EC10 |
| AUTH6 | `"mario.rossi@example.com"` (esistente) | `"wrong_password"` | `AuthenticationError` | utente esistente, password hash non corrispondente | EC5, EC10 |
| AUTH7 | `"inactive.user"` (esistente) | `"correct_password"` | `AuthenticationError` (utente inattivo) | utente esistente con `is_active=False` | EC4, EC11, EC12 |
| AUTH8 | `"inactive.user@example.com"` (esistente) | `"correct_password"` | `AuthenticationError` (utente inattivo) | utente esistente, email verificata con `is_active=False` | EC5, EC11, EC12 |
| AUTH9 | `"unverified.user@example.com"` (esistente) | `"correct_password"` | `AuthenticationError` (email non verificata) | utente esistente e attivo con `is_email_verified=False` | EC5, EC11, EC13 |
| AUTH10 | `"unverified.user"` (esistente) | `"correct_password"` | `AuthenticationError` (email non verificata) | utente esistente e attivo con `is_email_verified=False` | EC4, EC11, EC13 |
| AUTH11 | `""` (stringa vuota) | `"any_password"` | `AuthenticationError` | nessun utente può corrispondere a stringa vuota | EC1 |
| AUTH12 | `"mario.rossi"` (esistente) | `""` (stringa vuota) | `AuthenticationError` | utente esistente e attivo, nessuna password può corrispondere a stringa vuota | EC4, EC9 |
| AUTH13 | `"mario.rossi@example.com"` (esistente) | `""` (stringa vuota) | `AuthenticationError` | utente esistente e attivo, email verificata, nessuna password può corrispondere a stringa vuota | EC5, EC9 |
| AUTH14 | `""` (stringa vuota) | `""` (stringa vuota) | `AuthenticationError` | nessun utente e nessuna password possono corrispondere a stringa vuota | EC1, EC9 |
| AUTH15 | `" mario.rossi@example.com "` (email con spazio iniziale e finale) | `"correct_password"` | restituisce `User` (associato ad email: `"mario.rossi@example.com"`) | utente esistente e attivo, email verificata, password hash corrispondente | EC6, EC11, EC14 |
| AUTH16 | `"Mario.Rossi@Example.Com"` (email con caratteri upper case) | `"correct_password"` | restituisce `User` (associato ad email: `"mario.rossi@example.com"`) | utente esistente e attivo, email verificata, password hash corrispondente | EC7, EC11, EC14 |
| AUTH17 | `" mario.rossi "` (username con spazio iniziale e finale) | `"correct_password"` | restituisce `User` (associato ad username: `"mario.rossi"`) | utente esistente e attivo, password hash corrispondente | EC8, EC11, EC14 |

## 2 `participium.core.utils.parse_date`

Suggested test file: `test_parse_date.py`

Prototype: `parse_date(value: str | None) -> datetime | None`

**Requirements**:

Il sistema deve interpretare una stringa come datetime ISO-8601 e restituire il corrispondente oggetto `datetime`.

Se il valore è `None` o una stringa vuota, il sistema deve restituire `None`.

Se il valore è una stringa non conforme al formato ISO-8601, il sistema deve sollevare `ValueError`.

Se il valore rappresenta una data o un orario non valido nel calendario (es. mese fuori range, giorno inesistente, anno non bisestile), il sistema deve sollevare `ValueError`.

**Criterion**:
- value

**Predicates**:
- value è None → None
- value è stringa vuota → None
- value è non vuoto, ISO-8601 valido → datetime
- value è non vuoto, ISO-8601 valido con sola data (completezza minima) → datetime
- value è non vuoto, ISO-8601 valido con data e ora senza minuti e secondi → datetime
- value è non vuoto, ISO-8601 valido con data, ora e minuti senza secondi → datetime
- value è non vuoto, ISO-8601 non valido (formato generico) → ValueError
- value ha separatore di data errato (`/` invece di `-`) → ValueError
- value ha mese fuori range [1, 12] → ValueError
- value ha giorno fuori range [1, 31] → ValueError
- value ha componenti della data mancanti (formato incompleto) → ValueError
- value ha ora fuori range [0, 23] → ValueError
- value ha secondi negativi → ValueError
- value è sintatticamente valido ma rappresenta una data inesistente nel calendario → ValueError

**Equivalence Classes**

Per value:

- EC1: None
- EC2: stringa vuota
- EC3: non vuoto, ISO-8601 valido
- EC4: non vuoto, ISO-8601 non valido (qualsiasi forma)

| TC-ID | value | Expected | Fixture | EC covered |
| :---- | :---- | :------- | :------ | :--------- |
| PD1 | `None` | `None` | — | EC1 |
| PD2 | `""` (stringa vuota) | `None` | — | EC2 |
| PD3 | `"2024-01-15T10:30:00"` (ISO-8601 con orario) | `datetime(2024, 1, 15, 10, 30, 0)` | — | EC3 |
| PD4 | `"not-a-date"` (stringa non valida) | `ValueError` | — | EC4 |


Boundary: sintassi e limiti del formato ISO-8601

Confini validi di completezza della data ISO e limiti logici del calendario (mesi, giorni, ore).

| TC-ID | value | Boundary covered | Expected | Fixture |
| :---- | :---- | :--------------- | :------- | :------ |
| PDB1 | `"2023-10-25"` | Valid ISO, minimum completeness (solo data) | `datetime(2023, 10, 25, 0, 0, 0)` | — |
| PDB2 | `"2023-10-25T10"` | Valid ISO, senza minuti e secondi | `datetime(2023, 10, 25, 10, 0, 0)` | — |
| PDB3 | `"2023-10-25T10:01"` | Valid ISO, senza secondi | `datetime(2023, 10, 25, 10, 1, 0)` | — |
| PDB4 | `"2023/10/25T10:00"` | Invalid, separatore errato (`/` invece di `-`) | `ValueError` | — |
| PDB5 | `"2023-00-25T10:00:00"` | Invalid boundary, mese < 1 (zero) | `ValueError` | — |
| PDB6 | `"2023-13-25T10:00:00"` | Invalid boundary, mese > 12 | `ValueError` | — |
| PDB7 | `"2023-10-00T10:00:00"` | Invalid boundary, giorno < 1 (zero) | `ValueError` | — |
| PDB8 | `"2023-10-32T10:00:00"` | Invalid boundary, giorno > 31 | `ValueError` | — |
| PDB9 | `"2023-10"` | Invalid boundary, data con valori mancanti | `ValueError` | — |
| PDB10 | `"2024-01-15T24:00:00"` | Invalid boundary, ora > 23 | `ValueError` | — |
| PDB11 | `"2024-01-15T00:00:-1"` | Invalid boundary, secondi < 0 | `ValueError` | — |
| PDB12 | `"2023-02-29T10:00:00"` | Invalid boundary, 29 Febbraio in anno non bisestile | `ValueError` | — |

## 3 `participium.core.status_flow.ensure_transition_allowed`

Suggested test file: `test_status_flow.py`

Prototype: `ensure_transition_allowed(current_status: ReportStatus, next_status: ReportStatus) -> bool`

Allowed transitions:
`Pending Approval -> Pending Approval | Assigned | Rejected`;
`Assigned -> Assigned | In Progress | Suspended | Resolved`;
`In Progress -> In Progress | Suspended | Resolved`;
`Suspended -> Suspended | In Progress | Resolved`;
`Rejected -> Rejected`;
`Resolved -> Resolved`.

**Requirements**:
Il sistema deve verificare se una transizione di stato di una segnalazione è consentita dal flusso di lavoro definito.

Il sistema deve restituire True quando la transizione richiesta è consentita, incluse le auto-transizioni (stato corrente uguale allo stato successivo).

Il sistema deve sollevare ValidationError quando la transizione richiesta non è consentita dalle regole del flusso di lavoro.


**Criterion**: 
- current_status

**Predicates**: 
- current_status is Pending Approval → valid state

- current_status is Assigned → valid state

- current_status is In Progress → valid state

- current_status is Suspended → valid state

- current_status is Rejected → valid state

- current_status is Resolved → valid state

**Criterion**: 
- next_status

**Predicates**:
- next_status is Pending Approval → valid state

- next_status is Assigned → valid state

- next_status is In Progress → valid state

- next_status is Suspended → valid state

- next_status is Rejected → valid state

- next_status is Resolved → valid state

**Equivalence Classes**

Per current_status:

- EC1: Pending Approval

- EC2: Assigned

- EC3: In Progress

- EC4: Suspended

- EC5: Rejected

- EC6: Resolved

Per next_status:

- EC7: Pending Approval

- EC8: Assigned

- EC9: In Progress

- EC10: Suspended

- EC11: Rejected

- EC12: Resolved

**Combinations of equivalence classes**

Poiché la funzione definisce una macchina a stati basata su due input, devono essere considerate tutte le 6×6=36 combinazioni del dominio valido per testare le transizioni consentite e quelle negate.

Transizioni consentite (Risultato atteso: True):

EC1 × (EC7, EC8, EC11)

EC2 × (EC8, EC9, EC10, EC12)

EC3 × (EC9, EC10, EC12)

EC4 × (EC10, EC9, EC12)

EC5 × (EC11)

EC6 × (EC12)

Transizioni negate (Risultato atteso: ValidationError):

Tutte le altre combinazioni non elencate sopra.

| TC-ID | current_status | next_status | Expected | Fixture | EC covered |
| :---- | :------------- | :---------- | :------- | :------ | :--------- |
| SF1 | `Pending Approval` | `Assigned` | `True` | — | EC1 × EC8 |
| SF2 | `Pending Approval` | `Rejected` | `True` | — | EC1 × EC11 |
| SF3 | `Pending Approval` | `Pending Approval` | `True` | — | EC1 × EC7 |
| SF4 | `Assigned` | `In Progress` | `True` | — | EC2 × EC9 |
| SF5 | `Assigned` | `Suspended` | `True` | — | EC2 × EC10 |
| SF6 | `Assigned` | `Resolved` | `True` | — | EC2 × EC12 |
| SF7 | `Assigned` | `Assigned` | `True` | — | EC2 × EC8 |
| SF8 | `In Progress` | `Suspended` | `True` | — | EC3 × EC10 |
| SF9 | `In Progress` | `Resolved` | `True` | — | EC3 × EC12 |
| SF10 | `In Progress` | `In Progress` | `True` | — | EC3 × EC9 |
| SF11 | `Suspended` | `In Progress` | `True` | — | EC4 × EC9 |
| SF12 | `Suspended` | `Resolved` | `True` | — | EC4 × EC12 |
| SF13 | `Suspended` | `Suspended` | `True` | — | EC4 × EC10 |
| SF14 | `Rejected` | `Rejected` | `True` | — | EC5 × EC11 |
| SF15 | `Resolved` | `Resolved` | `True` | — | EC6 × EC12 |
| SF16 | `Pending Approval` | `Resolved` | `ValidationError` | — | EC1 × EC12 |
| SF17 | `Pending Approval` | `Suspended` | `ValidationError` | — | EC1 × EC10 |
| SF18 | `Pending Approval` | `In Progress` | `ValidationError` | — | EC1 × EC9 |
| SF19 | `Assigned` | `Pending Approval` | `ValidationError` | — | EC2 × EC7 |
| SF20 | `Assigned` | `Rejected` | `ValidationError` | — | EC2 × EC11 |
| SF21 | `In Progress` | `Assigned` | `ValidationError` |  — | EC3 × EC8 |
| SF22 | `In Progress` | `Pending Approval` | `ValidationError` | — | EC3 × EC7 |
| SF23 | `In Progress` | `Rejected` | `ValidationError` | — | EC3 × EC11 |
| SF24 | `Suspended` | `Pending Approval` | `ValidationError` | — | EC4 × EC7 |
| SF25 | `Suspended` | `Assigned` | `ValidationError` | — | EC4 × EC8 |
| SF26 | `Suspended` | `Rejected` | `ValidationError` | — | EC4 × EC11 |
| SF27 | `Rejected` | `Assigned` | `ValidationError` | — | EC5 × EC8 |
| SF28 | `Rejected` | `In Progress` | `ValidationError` | — | EC5 × EC9 |
| SF29 | `Rejected` | `Suspended` | `ValidationError` | — | EC5 × EC10 |
| SF30 | `Rejected` | `Resolved` | `ValidationError` | — | EC5 × EC12 |
| SF31 | `Rejected` | `Pending Approval` | `ValidationError` | — | EC5 × EC7 |
| SF32 | `Resolved` | `Pending Approval` | `ValidationError` | — | EC6 × EC7 |
| SF33 | `Resolved` | `Assigned` | `ValidationError` | — | EC6 × EC8 |
| SF34 | `Resolved` | `In Progress` | `ValidationError` | — | EC6 × EC9 |
| SF35 | `Resolved` | `Suspended` | `ValidationError` | — | EC6 × EC10 |
| SF36 | `Resolved` | `Rejected` | `ValidationError` | — | EC6 × EC11 |

## 4 `participium.services.report_service.ReportService.create_report`

Suggested test file: `test_create_report.py`

Prototype: `create_report(reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False) -> Report`

**Requirements**:
Il sistema deve creare una nuova segnalazione civica associata al reporter autenticato fornito.

Il sistema deve sollevare ValidationError se category_id è assente, malformato, riferito a una categoria inesistente o a una categoria inattiva.

Il sistema deve sollevare ValidationError se title o description sono assenti o vuoti.

Il sistema deve sollevare ValidationError se latitude o longitude sono assenti o vuoti.

Il sistema deve sollevare ValidationError se latitude o longitude non sono convertibili a un valore numerico valido.

Il sistema deve sollevare ValidationError se le coordinate non rientrano nei limiti geografici validi (latitudine in [-90, 90], longitudine in [-180, 180]).

Il sistema deve sollevare ValidationError se non viene fornita almeno una foto con filename valido.

Il sistema deve sollevare ValidationError se vengono fornite più di 3 foto con filename valido.

Il sistema deve restituire la segnalazione creata e ricaricata dopo la persistenza come oggetto Report.

Se is_anonymous è True, la segnalazione deve nascondere pubblicamente il reporter.

**Criterion**:
- category_id

**Predicates**:
- category_id è mancante o nullo → invalid
- category_id è malformato → invalid
- category_id è sconosciuto → invalid
- category_id è inattivo → invalid
- category_id è valido e attivo → valid

**Criterion**:
- title & description

**Predicates**:
- campo è mancante (None) o vuoto → invalid
- campo è presente e valorizzato → valid

**Criterion**:
- latitude & longitude

**Predicates**:
- coordinata è mancante (None) o vuota → invalid
- coordinata è malformata (non numerica) → invalid
- coordinata è fuori dai confini geografici → invalid
- coordinata è un numero valido entro i confini → valid

**Criterion**:
- photos

**Predicates**:
- numero di foto valide == 0 → invalid
- numero di foto valide > 3 → invalid
- 1 <= numero di foto valide <= 3 → valid

**Equivalence Classes**

Per category_id:

- EC1: Valido, numerico o stringa convertibile, attivo

- EC2: Mancante / None

- EC3: Malformato (non convertibile a intero)

- EC4: Sconosciuto (ID inesistente)

- EC5: Categoria inattiva

Per campi di testo (title, description):

- EC6: Testo valido

- EC7: Mancante / None / Stringa vuota


Per coordinate (latitude, longitude):

- EC8: Valori numerici (o stringhe numeriche) nei limiti

- EC9: Mancante / None / Stringa vuota

- EC10: Valori malformati (es. "abc")

- EC11: Valori fuori dai limiti (es. lat > 90 o lon < -180)

Per photos:

- EC12: Lista con 1, 2 o 3 foto valide (con filename)

- EC13: Lista con 0 foto valide (lista vuota o tutti elementi senza filename)

- EC14: Lista con > 3 foto valide

**Combinations of equivalence classes**

Transizioni consentite (Risultato atteso: True):
- EC1 × EC6 × EC8 × EC12


Transizioni negate (Risultato atteso: ValidationError):

- EC2 × EC6 × EC8 × EC12 (Categoria mancante)

- EC3 × EC6 × EC8 × EC12 (Categoria malformata)

- EC4 × EC6 × EC8 × EC12 (Categoria sconosciuta)

- EC5 × EC6 × EC8 × EC12 (Categoria inattiva)

- EC1 × EC7 × EC8 × EC12 (Titolo o descrizione mancanti/vuoti)

- EC1 × EC6 × EC9 × EC12 (Coordinate mancanti/vuote)

- EC1 × EC6 × EC10 × EC12 (Coordinate malformate)

- EC1 × EC6 × EC11 × EC12 (Coordinate fuori dai confini geografici)

- EC1 × EC6 × EC8 × EC13 (Nessuna foto valida fornita)

- EC1 × EC6 × EC8 × EC14 (Più di 3 foto valide fornite)

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture | EC covered |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ | :--------- |
| CR1 | utente valido | `1` (int) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CR2 | utente valido | `"1"` (str) | `"Buca"` | `"Descrizione"` | `"45.0"` | `"9.0"` | 1 foto valida | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CR3 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | ` 9.0 ` | 1 foto valida | `True` | `Report` con `is_anonymous=True` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CR4 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `"45.0"(string)` | `9.0` | 1 foto valida | `False` | `Report`  | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CR5 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `"9.0"(string)` | 1 foto valida | `False` | `Report`  | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CR6 | utente valido | `None` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo | EC2 × EC6 × EC8 × EC12 |
| CR7 | utente valido | `"abc"` (malformato) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo | EC3 × EC6 × EC8 × EC12 |
| CR8 | utente valido | `9999` (sconosciuta) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, nessuna categoria con id=9999 | EC4 × EC6 × EC8 × EC12 |
| CR9 | utente valido | `2` (inattiva) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria inattiva con id=2 | EC5 × EC6 × EC8 × EC12 |
| CR10 | utente valido | `1` | `None` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC7 × EC8 × EC12 |
| CR11 | utente valido | `1` | `"Buca"` | `None` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC7 × EC8 × EC12 |
| CR12 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `None` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC9 × EC12 |
| CR13 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `None` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC9 × EC12 |
| CR14 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `"abc"` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC10 × EC12 |
| CR15 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `"abc"` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC10 × EC12 |
| CR16 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 FileStorage senza filename | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC13 |

**Boundary: numero di foto valide**
Il contratto impone minimo 1 e massimo 3 foto con filename.

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture | EC covered |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ | :--------- |
| CRB1 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 2 foto (entrambe senza filename) | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC13 |
| CRB2 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida (minimo) | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CRB3 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 3 foto valide (massimo) | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CRB4 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 4 foto valide (oltre massimo) | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC14 |  
| CRB5 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | [ ] (0 foto, lista vuota) | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC13 |
| CRB6 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 4 foto (2 con filename, 2 senza) | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 (le foto valide sono 2, quindi entro i limiti) |

**Boundary: campi vuoti**
Test del confine strutturale inferiore (stringa vuota).

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture | EC covered |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ | :--------- |
| CRB7 | utente valido | `1` | `""` | `"Descrizione"` | `45.0` | `9.0` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC7 × EC8 × EC12 |
| CRB8 | utente valido | `1` | `"Buca"` | `""` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC7 × EC8 × EC12 |
| CRB9 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `""` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC9 × EC12 |
| CRB10 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `""` | 1 foto valida| `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC9 × EC12 |
| CRB11 | utente valido | `""` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida| `False` | `ValidationError` | utente attivo | EC2 × EC6 × EC8 × EC12 |

**Boundary: limiti geografici**
Test dei limiti geografici (Latitudinte [-90, 90], Longitudine [-180, 180]).

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture | EC covered |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ | :--------- |
| CRB12 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `-90.0` | `0.0` | 1 foto | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CRB13 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `-90.1` | `0.0` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC11 × EC12 |
| CRB14 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `90.0` | `0.0` | 1 foto | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CRB15 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `90.1` | `0.0` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC11 × EC12 |
| CRB16 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `-180.0` | 1 foto | `False` | `Report` | utente attivo, categoria attiva | EC1 × EC6 × EC8 × EC12 |
| CRB17 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `-180.1` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC11 × EC12 |
| CRB18 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `180.0` | 1 foto | `False` | `Report` | utente attivo, categoria attiva| EC1 × EC6 × EC8 × EC12 |
| CRB19 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `180.1` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva | EC1 × EC6 × EC11 × EC12 |

## 5 `participium.services.report_service.ReportService.update_status`

Suggested test file: `test_update_status.py`

Prototype: `update_status(report_id: int, operator: User, next_status_value: str, note: str | None = None) -> Report`

**Requirements**: Il sistema deve aggiornare lo stato di una segnalazione esistente, verificando autorizzazioni e validità.     

Il sistema deve sollevare: AuthorizationError se l'operatore non ha i permessi per cambiare lo stato della segnalazione.        

Il sistema deve sollevare: NotFoundError se la segnalazione non esiste.     

Il sistema deve sollevare: ValidationError se il valore in 'next_status_value' non è ammesso.     

Il sistema deve sollevare: ValidationError se la transizione non è consentita (ensure_transition_allowed).      

Il sistema solleva: ValidationError se si mette stato "Rejected" senza 'note'.      


**Criterion:**
- report_id  

**Predicates**:     
- report_id esistente -> valid      
- reposrt_id non esistente -> invalid



**Criterion:**
- operator     

**Predicates**:     
- operator esistente con ruolo operatore -> valid       
- operator con ruolo cittadino -> invalid       
- operator non esistente -> invalid



**Criterion:**
- next_status_value   

**Predicates**:
- next_status_value valore valido di ReportStatus -> valid 
- next_status_value valore invalido -> invalid



**Criterion:**
- note      

**Predicates**:
- note: presente se next_status_value == "Rejected" -> valid 
- note valore assente se next_status_value == "Rejected" -> invalid 
- note qualunque valore negli altri casi -> valid


**Equivalence classes**     
- EC1: report_id esistente
- EC2: report_id non esistente
- EC3: operator esistente
- EC4: operator citizen
- EC5: operator non esistente
- EC6: next_status_value valido
- EC7: next_status_value invalido
- EC8: note presente (per Rejected)
- EC9: note assente (per Rejected)
- EC10: note qualsiasi (per stati non Rejected)


**Combinations of equivalence classes**     
Transizioni consentite:         
- EC1 x EC3 x EC6 x EC10
- EC1 x EC3 x EC6 x EC8
- EC1 x EC3 x EC6 x EC9

Transizioni negate:
- EC2 x EC3 x EC6 x EC10 (report non esistente NotFoundError)
- EC1 x EC4 x EC6 x EC10 (operatore non ha permessi AuthorizationError)
- EC1 x EC5 x EC6 x EC10 (operatore non esistente)


| TC-ID | report_id | operator | next_status_value | note | Expected | Fixture |
| :---- | :-------- | :------- | :---------------- | :--- | :------- | :------ |
|  |  |  |  |  |  |  |

## 6 `participium.services.report_service.ReportService.list_public_reports`

Suggested test file: `test_public_reports.py`

Prototype: `list_public_reports(category_id: int | None = None, status: ReportStatus | None = None, date_from: datetime | None = None, date_to: datetime | None = None, sort: str = "desc") -> list[Report]`

| TC-ID | category_id | status | date_from | date_to | sort | Expected | Fixture |
| :---- | :---------- | :----- | :-------- | :------ | :--- | :------- | :------ |
|  |  |  |  |  |  |  |  |


## 7 `participium.services.messaging_service.MessagingService.send_message`

Suggested test file: `test_send_message.py`

Prototype: `send_message(report: Report, sender: User, body: str) -> Message`

**Requirements**:

Il sistema deve permettere l'invio di messaggi all'interno di una conversazione legata a una segnalazione.

Deve sollevare `AuthorizationError` se il mittente non ha accesso alla conversazione.

Deve sollevare `ValidationError` se il corpo del messaggio è vuoto o composto solo da spazi dopo il trimming.

Deve sollevare `ValidationError` se non è possibile individuare un destinatario valido per la conversazione.

**Criterion**:
- sender access

**Predicates**:
- sender è l'autore del report (`reporter_id == sender.id`) → valido (continua)
- sender ha ruolo `OPERATOR` o `ADMIN` → valido (continua)
- sender non è l'autore del report né ha ruolo `OPERATOR`/`ADMIN` → non valido (`AuthorizationError`)

**Criterion**:
- body content (quando sender è autorizzato)

**Predicates**:
- body non vuoto dopo `strip()` → valido (continua)
- body vuoto (`""`) o composto solo da whitespace → non valido (`ValidationError`)

**Criterion**:
- recipient resolution (quando sender è autorizzato e body è valido)

**Predicates**:
- sender ha ruolo `OPERATOR`/`ADMIN` → destinatario è `report.reporter` → risolvibile (continua)
- sender è `CITIZEN` e almeno un messaggio precedente nella thread è stato inviato da un `OPERATOR`/`ADMIN` → risolvibile (continua)
- sender è `CITIZEN` e almeno un evento in `report.status_history` ha `changed_by.role` in `{OPERATOR, ADMIN}` → risolvibile (continua)
- sender ha ruolo `OPERATOR`/`ADMIN` ma `report.reporter` è `None` → non risolvibile (`ValidationError`)

**Equivalence Classes**

- EC1: Mittente autorizzato (autore del report oppure ruolo `OPERATOR`/`ADMIN`)
- EC2: Mittente non autorizzato (ruolo `CITIZEN` estraneo al report)
- EC3: Body valido (non vuoto dopo `strip()`)
- EC4: Body non valido (vuoto o solo whitespace dopo `strip()`)
- EC5: Destinatario risolvibile
- EC6: Destinatario non risolvibile (`_resolve_recipient` restituisce `None`)

Nota: la combinazione EC2 × EC6 non è testabile in isolamento perché un mittente non autorizzato (EC2) causa `AuthorizationError` prima che venga tentata la risoluzione del destinatario.

**Combinations of equivalence classes**

    EC1 × EC3 × EC5
    EC2 × EC3 × EC5
    EC1 × EC4 × EC5
    EC1 × EC3 × EC6

| TC-ID | report | sender | body | Expected | Fixture | EC covered |
| :---- | :----- | :----- | :--- | :------- | :------ | :--------- |
| MSG1 | `Report(id=1, reporter_id=10, reporter=REPORTER)` | `User(id=10, role=CITIZEN)` | `"Ciao, il problema persiste."` | `Message` | Report persistito, mittente è l'autore, operatore risolvibile via `status_history`. | EC1 × EC3 × EC5 |
| MSG2 | `Report(id=1, reporter_id=10, reporter=REPORTER)` | `User(id=99, role=CITIZEN)` | `"Ciao"` | `AuthorizationError` | Utente id=99 estraneo al report (reporter_id=10), nessun ruolo privilegiato. | EC2 × EC3 × EC5 |
| MSG3 | `Report(id=1, reporter_id=10, reporter=REPORTER)` | `User(id=10, role=CITIZEN)` | `"   "` | `ValidationError` | Body composto solo da spazi, blank dopo `strip()`. | EC1 × EC4 × EC5 |
| MSG4 | `Report(id=1, reporter_id=10, reporter=REPORTER)` | `User(id=10, role=CITIZEN)` | `""` | `ValidationError` | Body stringa vuota. | EC1 × EC4 × EC5 |
| MSG5 | `Report(id=2, reporter_id=None, reporter=None, status_history=[])` | `User(id=20, role=OPERATOR)` | `"Aggiornamento."` | `ValidationError` | Mittente operatore autorizzato, ma `report.reporter` è `None`: `_resolve_recipient` restituisce `None`. | EC1 × EC3 × EC6 |
| MSG6 | `Report(id=1, reporter_id=10, reporter=REPORTER)` | `User(id=20, role=OPERATOR)` | `"Abbiamo preso in carico la segnalazione."` | `Message` | Mittente operatore; il destinatario è sempre `report.reporter`. | EC1 × EC3 × EC5 |

**Boundary: body dopo trimming**

| TC-ID | report | sender | body | Expected | Fixture | EC covered |
| :---- | :----- | :----- | :--- | :------- | :------ | :--------- |
| MSGB1 | `Report(id=1, reporter_id=10, reporter=REPORTER)` | `User(id=10, role=CITIZEN)` | `" "` (singolo spazio) | `ValidationError` | Body non vuoto ma blank dopo `strip()`. | EC1 × EC4 × EC5 |
| MSGB2 | `Report(id=1, reporter_id=10, reporter=REPORTER)` | `User(id=10, role=CITIZEN)` | `"\t\n"` (tab e newline) | `ValidationError` | Body con soli caratteri whitespace, blank dopo `strip()`. | EC1 × EC4 × EC5 |

---

## 8 `participium.core.security.verify_password`

Suggested test file: `test_verify_password.py`

Prototype: `verify_password(password: str, password_hash: str) -> bool`

**Requirements**:

Il sistema deve verificare la corrispondenza tra una password in chiaro e un hash memorizzato, restituendo un booleano.

Non sono documentate eccezioni di dominio.

**Criterion**:
- password match

**Predicates**:
- `password` corrisponde all'`password_hash` → `True`
- `password` non corrisponde all'`password_hash` → `False`

**Equivalence Classes**

- EC1: Match (`password` corrisponde all'hash → `True`)
- EC2: Mismatch (`password` non corrisponde all'hash → `False`)

| TC-ID | password | password_hash | Expected | Fixture | EC covered |
| :---- | :------- | :------------ | :------- | :------ | :--------- |
| PWD1 | `"secure123"` | `"hash_di_secure123"` | `True` | Password e hash corrispondono. | EC1 |
| PWD2 | `"wrong_pass"` | `"hash_di_secure123"` | `False` | Password errata, hash invariato. | EC2 |

**Boundary: input strutturalmente vuoti**

Il contratto non documenta il comportamento su stringhe vuote; i test seguenti verificano l'ipotesi ragionevole che nessuna password corrisponda a un hash vuoto e viceversa.

| TC-ID | password | password_hash | Expected | Fixture | EC covered |
| :---- | :------- | :------------ | :------- | :------ | :--------- |
| PWDB1 | `""` | `"hash_di_secure123"` | `False` | Password vuota: per nessun algoritmo di hashing standard `""` produce `hash_di_secure123`. | EC2 |
| PWDB2 | `"secure123"` | `""` | `False` | Hash vuoto: nessuna password in chiaro produce una stringa vuota come hash. | EC2 |
| PWDB3 | `""` | `""` | `False` | Entrambi vuoti: una stringa vuota non è un hash valido di alcuna password. | EC2 |

## 9 `participium.services.notification_service.NotificationService.create_notification`

Suggested test file: `test_create_notification.py`

Prototype: `create_notification(user: User | None, notification_type: NotificationType, title: str, body: str, report: Report | None = None) -> Notification | None`

| TC-ID | user | notification_type | title | body | report | Expected | Fixture |
| :---- | :--- | :---------------- | :---- | :--- | :----- | :------- | :------ |
|  |  |  |  |  |  |  |  |

## 10 `participium.services.user_service.UserService.update_profile`

Suggested test file: `test_update_profile.py`

Prototype: `update_profile(user: User, username: str | None = None, first_name: str | None = None, last_name: str | None = None, email_notifications_enabled: bool | None = None, profile_picture: FileStorage | None = None) -> User`

| TC-ID | user | username | first_name | last_name | email_notifications_enabled | profile_picture | Expected | Fixture |
| :---- | :--- | :------- | :--------- | :-------- | :-------------------------- | :-------------- | :------- | :------ |
|  |  |  |  |  |  |  |  |  |
