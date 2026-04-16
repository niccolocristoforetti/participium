## 1 `participium.services.auth_service.AuthService.authenticate`

Suggested test file: `test_authenticate.py`

Prototype: `authenticate(identifier: str, password: str) -> User`

| TC-ID | identifier | password | Expected | Fixture |
| :---- | :--------- | :------- | :------- | :------ |
| AUTH1 | `"mario.rossi"` (username valido) | `"correct_password"` | restituisce `User` (associato ad username: `"mario.rossi"`) | utente esistente e attivo, password hash corrispondente |
| AUTH2 | `"mario.rossi@example.com"` (email valida) | `"correct_password"` | restituisce `User` (associato ad email: `"mario.rossi@example.com"`) | utente esistente e attivo, email verificata, password hash corrispondente |
| AUTH3 | `"unknown_user"` (non esistente) | `"any_password"` | `AuthenticationError` | Nessun utente nel Database con username associata: `"unknown_user" |
| AUTH4 | `"unknown_user@example.com"` (non esistente) | `"any_password"` | `AuthenticationError` | Nessun utente nel Database con email associata: `"unknown_user" |
| AUTH5 | `"mario.rossi"` (esistente) | `"wrong_password"` | `AuthenticationError` | utente esistente e attivo, password hash non corrispondente |
| AUTH6 | `"mario.rossi@example.com"` (esistente) | `"wrong_password"` | `AuthenticationError` | utente esistente e attivo, password hash non corrispondente |
| AUTH7 | `"inactive.user"` (esistente) | `"correct_password"` | `AuthenticationError` (utente inattivo) | utente esistente con `is_active=False` |ù
| AUTH8 | `"inactive.user@example.com"` (esistente) | `"correct_password"` | `AuthenticationError` (utente inattivo) | utente esistente, email verificata con `is_active=False` |
| AUTH9 | `"unverified.user@example.com"` (esistente) | `"correct_password"` | `AuthenticationError` (email non verificata) | utente esistente e attivo con `is_email_verified=False` |
| AUTH10 | `"unverified.user"` (esistente) | `"correct_password"` | `AuthenticationError` (email non verificata) | utente esistente e attivo con `is_email_verified=False` |
| AUTH10 | `""` (stringa vuota) | `"any_password"` | `AuthenticationError` | nessun utente può corrispondere a stringa vuota |
| AUTH11 | `"mario.rossi"` (esistente) | `""` (stringa vuota) | `AuthenticationError` | utente esistente e attivo, nessuna password può corrispondere a stringa vuota |
| AUTH12 | `"mario.rossi@example.com"` (esistente) | `""` (stringa vuota) | `AuthenticationError` | utente esistente e attivo, email verificata, nessuna password può corrispondere a stringa vuota |
| AUTH13 | `""` (stringa vuota) | `""` (stringa vuota) | `AuthenticationError` | nessun utente e nessuna password possono corrispondere a stringa vuota |

## 2 `participium.core.utils.parse_date`

Suggested test file: `test_parse_date.py`

Prototype: `parse_date(value: str | None) -> datetime | None`

| TC-ID | value | Expected | Fixture |
| :---- | :---- | :------- | :------ |
|  |  |  |  |

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
|  |  |  |  |  |

## 4 `participium.services.report_service.ReportService.create_report`

Suggested test file: `test_create_report.py`

Prototype: `create_report(reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False) -> Report`

| TC-ID | reporter | category_id | title | description | latitude | longitude | photos | is_anonymous | Expected | Fixture |
| :---- | :------- | :---------- | :---- | :---------- | :------- | :-------- | :----- | :----------- | :------- | :------ |
|  |  |  |  |  |  |  |  |  |  |  |

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
