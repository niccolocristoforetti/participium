## 1 `participium.services.auth_service.AuthService.authenticate`

Suggested test file: `test_authenticate.py`

Prototype: `authenticate(identifier: str, password: str) -> User`

| TC-ID | identifier | password | Expected | Fixture |
| :---- | :--------- | :------- | :------- | :------ |
| AUTH1 | `"mario.rossi"` (username valido) | `"correct_password"` | restituisce `User` (associato ad username: `"mario.rossi"`) | utente esistente e attivo, password hash corrispondente |
| AUTH2 | `"mario.rossi@example.com"` (email valida) | `"correct_password"` | restituisce `User` (associato ad email: `"mario.rossi@example.com"`) | utente esistente e attivo, email verificata, password hash corrispondente |
| AUTH3 | `"unknown_user"` (non esistente) | `"any_password"` | `AuthenticationError` | Nessun utente nel Database con username associata: `"unknown_user"` |
| AUTH4 | `"unknown_user@example.com"` (non esistente) | `"any_password"` | `AuthenticationError` | Nessun utente nel Database con email associata: `"unknown_user"` |
| AUTH5 | `"mario.rossi"` (esistente) | `"wrong_password"` | `AuthenticationError` | utente esistente, password hash non corrispondente |
| AUTH6 | `"mario.rossi@example.com"` (esistente) | `"wrong_password"` | `AuthenticationError` | utente esistente, password hash non corrispondente |
| AUTH7 | `"inactive.user"` (esistente) | `"correct_password"` | `AuthenticationError` (utente inattivo) | utente esistente con `is_active=False` |
| AUTH8 | `"inactive.user@example.com"` (esistente) | `"correct_password"` | `AuthenticationError` (utente inattivo) | utente esistente, email verificata con `is_active=False` |
| AUTH9 | `"unverified.user@example.com"` (esistente) | `"correct_password"` | `AuthenticationError` (email non verificata) | utente esistente e attivo con `is_email_verified=False` |
| AUTH10 | `"unverified.user"` (esistente) | `"correct_password"` | `AuthenticationError` (email non verificata) | utente esistente e attivo con `is_email_verified=False` |
| AUTH11 | `""` (stringa vuota) | `"any_password"` | `AuthenticationError` | nessun utente può corrispondere a stringa vuota |
| AUTH12 | `"mario.rossi"` (esistente) | `""` (stringa vuota) | `AuthenticationError` | utente esistente e attivo, nessuna password può corrispondere a stringa vuota |
| AUTH13 | `"mario.rossi@example.com"` (esistente) | `""` (stringa vuota) | `AuthenticationError` | utente esistente e attivo, email verificata, nessuna password può corrispondere a stringa vuota |
| AUTH14 | `""` (stringa vuota) | `""` (stringa vuota) | `AuthenticationError` | nessun utente e nessuna password possono corrispondere a stringa vuota |

## 2 `participium.core.utils.parse_date`

Suggested test file: `test_parse_date.py`

Prototype: `parse_date(value: str | None) -> datetime | None`

| TC-ID | value | Expected | Fixture |
| :---- | :---- | :------- | :------ |
| PD1 | `None` | `None` | — |
| PD2 | `""` (stringa vuota) | `None` | — |
| PD3 | `"2024-01-15T10:30:00"` (ISO-8601 con orario) | `datetime(2024, 1, 15, 10, 30, 0)` | — |
| PD4 | `"not-a-date"` (stringa non valida) | `ValueError` | — |


**Boundary: sintassi e limiti del formato ISO-8601**
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

| TC-ID | current_status | next_status | Expected | Fixture |
| :---- | :------------- | :---------- | :------- | :------ |
| SF1 | `Pending Approval` | `Assigned` | `True` | — |
| SF2 | `Pending Approval` | `Rejected` | `True` | — |
| SF3 | `Pending Approval` | `Pending Approval` | `True` | — |
| SF4 | `Assigned` | `In Progress` | `True` | — |
| SF5 | `Assigned` | `Suspended` | `True` | — |
| SF6 | `Assigned` | `Resolved` | `True` | — |
| SF7 | `Assigned` | `Assigned` | `True` | — |
| SF8 | `In Progress` | `Suspended` | `True` | — |
| SF9 | `In Progress` | `Resolved` | `True` | — |
| SF10 | `In Progress` | `In Progress` | `True` | — |
| SF11 | `Suspended` | `In Progress` | `True` | — |
| SF12 | `Suspended` | `Resolved` | `True` | — |
| SF13 | `Suspended` | `Suspended` | `True` | — |
| SF14 | `Rejected` | `Rejected` | `True` | — |
| SF15 | `Resolved` | `Resolved` | `True` | — |
| SF16 | `Pending Approval` | `Resolved` | `ValidationError` | — |
| SF17 | `Pending Approval` | `Suspended` | `ValidationError` | — |
| SF18 | `Pending Approval` | `In Progress` | `ValidationError` | — |
| SF19 | `Assigned` | `Pending Approval` | `ValidationError` | — |
| SF20 | `Assigned` | `Rejected` | `ValidationError` | — |
| SF21 | `In Progress` | `Assigned` | `ValidationError` | — |
| SF22 | `In Progress` | `Pending Approval` | `ValidationError` | — |
| SF23 | `In Progress` | `Rejected` | `ValidationError` | — |
| SF24 | `Suspended` | `Pending Approval` | `ValidationError` | — |
| SF25 | `Suspended` | `Assigned` | `ValidationError` | — |
| SF26 | `Suspended` | `Rejected` | `ValidationError` | — |
| SF27 | `Rejected` | `Assigned` | `ValidationError` | — |
| SF28 | `Rejected` | `In Progress` | `ValidationError` | — |
| SF29 | `Rejected` | `Suspended` | `ValidationError` | — |
| SF30 | `Rejected` | `Resolved` | `ValidationError` | — |
| SF31 | `Rejected` | `Pending Approval` | `ValidationError` | — |
| SF32 | `Resolved` | `Pending Approval` | `ValidationError` | — |
| SF33 | `Resolved` | `Assigned` | `ValidationError` | — |
| SF34 | `Resolved` | `In Progress` | `ValidationError` | — |
| SF35 | `Resolved` | `Suspended` | `ValidationError` | — |
| SF36 | `Resolved` | `Rejected` | `ValidationError` | — |

## 4 `participium.services.report_service.ReportService.create_report`

Suggested test file: `test_create_report.py`

Prototype: `create_report(reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False) -> Report`

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ |
| CR1 | utente valido | `1` (int) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `Report` | utente attivo, categoria attiva |
| CR2 | utente valido | `"1"` (str) | `"Buca"` | `"Descrizione"` | `"45.0"` | `"9.0"` | 1 foto valida | `False` | `Report` | utente attivo, categoria attiva |
| CR3 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | ` 9.0 ` | 1 foto valida | `True` | `Report` con `is_anonymous=True` | utente attivo, categoria attiva |
| CR4 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `"45.0"(string)` | `9.0` | 1 foto valida | `False` | `Report`  | utente attivo, categoria attiva |
| CR5 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `"9.0"(string)` | 1 foto valida | `False` | `Report`  | utente attivo, categoria attiva |
| CR6 | utente valido | `None` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo |
| CR7 | utente valido | `"abc"` (malformato) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo |
| CR8 | utente valido | `9999` (sconosciuta) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, nessuna categoria con id=9999 |
| CR9 | utente valido | `2` (inattiva) | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria inattiva con id=2 |
| CR10 | utente valido | `1` | `None` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva |
| CR11 | utente valido | `1` | `"Buca"` | `None` | `45.0` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva |
| CR12 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `None` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva |
| CR13 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `None` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva |
| CR14 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `"abc"` | `9.0` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva |
| CR15 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `"abc"` | 1 foto valida | `False` | `ValidationError` | utente attivo, categoria attiva |
| CR16 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 FileStorage senza filename | `False` | `ValidationError` | utente attivo, categoria attiva |

**Boundary: numero di foto valide**
Il contratto impone minimo 1 e massimo 3 foto con filename.

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ |
| CRB1 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 0 foto valide | `False` | `ValidationError` | utente attivo, categoria attiva |
| CRB2 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 1 foto valida (minimo) | `False` | `Report` | utente attivo, categoria attiva |
| CRB3 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 3 foto valide (massimo) | `False` | `Report` | utente attivo, categoria attiva |
| CRB4 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `9.0` | 4 foto valide (oltre massimo) | `False` | `ValidationError` | utente attivo, categoria attiva |

**Boundary: campi vuoti**
Test del confine strutturale inferiore (stringa vuota).

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ |
| CRB5 | utente valido | `1` | `""` | `"Descrizione"` | `45.0` | `9.0` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva |
| CRB6 | utente valido | `1` | `"Buca"` | `""` | `45.0` | `9.0` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva |
| CRB7 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `""` | `9.0` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva |
| CRB8 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `45.0` | `""` | 1 foto | `False` | `ValidationError` | utente attivo, categoria attiva |

**Boundary: limiti geografici**
Test dei limiti geografici (Latitudinte [-90, 90], Longitudine [-180, 180]).

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ |
| CRB9 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `-90.0` | `0.0` | 1 foto | `False` | `Report` | Limite minimo latitudine |
| CRB10 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `-90.1` | `0.0` | 1 foto | `False` | `ValidationError` | Oltre limite minimo latitudine |
| CRB11 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `90.0` | `0.0` | 1 foto | `False` | `Report` | Limite massimo latitudine |
| CRB12 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `90.1` | `0.0` | 1 foto | `False` | `ValidationError` | Oltre limite massimo latitudine |
| CRB13 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `-180.0` | 1 foto | `False` | `Report` | Limite minimo longitudine |
| CRB14 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `-180.1` | 1 foto | `False` | `ValidationError` | Oltre limite minimo longitudine |
| CRB15 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `180.0` | 1 foto | `False` | `Report` | Limite massimo longitudine |
| CRB16 | utente valido | `1` | `"Buca"` | `"Descrizione"` | `0.0` | `180.1` | 1 foto | `False` | `ValidationError` | Oltre limite massimo longitudine |

## 5 `participium.services.report_service.ReportService.update_status`

Suggested test file: `test_update_status.py`

Prototype: `update_status(report_id: int, operator: User, next_status_value: str, note: str | None = None) -> Report`

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

| TC-ID | report | sender | body | Expected | Fixture |
| :---- | :----- | :----- | :--- | :------- | :------ |
|  |  |  |  |  |  |

## 8 `participium.core.security.verify_password`

Suggested test file: `test_verify_password.py`

Prototype: `verify_password(password: str, password_hash: str) -> bool`

| TC-ID | password | password_hash | Expected | Fixture |
| :---- | :------- | :------------ | :------- | :------ |
|  |  |  |  |  |

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
