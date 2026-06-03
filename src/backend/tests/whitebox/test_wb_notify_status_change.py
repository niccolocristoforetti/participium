from __future__ import annotations

from unittest.mock import Mock, call
import pytest

from participium.models.enums import NotificationType, Role
from participium.models.report import Report
from participium.models.user import User
from participium.services.notification_service import NotificationService


pytestmark = pytest.mark.whitebox



#  Helpers 


# istanzia un oggetto utente mockato con id e ruolo specifici.
def _user(*, user_id: int, role: Role = Role.CITIZEN) -> User:
    return User(id=user_id, username=f"user{user_id}", role=role)


# istanzia un oggetto report mockato con un id specifico.
def _report(*, report_id: int) -> Report:
    return Report(id=report_id)



#  Fixtures 


# Prepara l'ambiente isolando NotificationService e mockando il metodo create_notification.
@pytest.fixture
def notification_service() -> NotificationService:
    service = NotificationService(
        session=Mock(),
        notification_repository=Mock(),
        email_gateway=Mock(),
    )
    service.create_notification = Mock()
    return service



#  Casi di Test 


# NSC1 – Caso base singolo destinatario: verifica che la notifica sia correttamente creata per un singolo utente valido.
def test_nsc1_notify_status_change_creates_notification_for_single_recipient(
    notification_service: NotificationService,
) -> None:
    service = notification_service
    recipient = _user(user_id=1)
    report = _report(report_id=10)
    body = "Stato aggiornato"

    service.notify_status_change([recipient], report, body)

    service.create_notification.assert_called_once_with(
        recipient,
        NotificationType.STATUS_CHANGE,
        f"Report #{report.id} status updated",
        body,
        report=report,
    )


# NSC2 – Gestione valori nulli: verifica che gli elementi None all'interno della lista dei destinatari vengano saltati senza sollevare eccezioni.
def test_nsc2_notify_status_change_skips_none_recipients(
    notification_service: NotificationService,
) -> None:
    service = notification_service
    report = _report(report_id=1)

    service.notify_status_change([None], report, "body")

    service.create_notification.assert_not_called()


# NSC3 – Rimozione duplicati: verifica che nel caso di id utente ripetuti, la notifica sia inviata una sola volta per ciascun utente univoco.
def test_nsc3_notify_status_change_skips_duplicate_recipient_ids(
    notification_service: NotificationService,
) -> None:
    service = notification_service
    recipient1 = _user(user_id=2)
    recipient2 = _user(user_id=2)
    report = _report(report_id=12)
    body = "Stato aggiornato"

    service.notify_status_change([recipient1, recipient2], report, body)

    service.create_notification.assert_called_once_with(
        recipient1,
        NotificationType.STATUS_CHANGE,
        f"Report #{report.id} status updated",
        body,
        report=report,
    )


# NSCB1 – Caso limite lista vuota: verifica il comportamento del sistema quando viene passata una lista di destinatari vuota (0 iterazioni del ciclo).
def test_nscb1_notify_status_change_handles_empty_recipient_list(
    notification_service: NotificationService,
) -> None:
    service = notification_service
    report = _report(report_id=13)

    service.notify_status_change([], report, "body")

    service.create_notification.assert_not_called()


# NSC4 – Destinatari multipli univoci: verifica che la notifica venga recapitata singolarmente a ciascun utente presente nella lista quando sono tutti distinti.
def test_nsc4_notify_status_change_sends_notification_to_multiple_unique_recipients(
    notification_service: NotificationService,
) -> None:
    service = notification_service
    recipient1 = _user(user_id=3)
    recipient2 = _user(user_id=4)
    report = _report(report_id=14)
    body = "Stato aggiornato"

    service.notify_status_change([recipient1, recipient2], report, body)

    assert service.create_notification.call_count == 2
    service.create_notification.assert_has_calls(
        [
            call(
                recipient1,
                NotificationType.STATUS_CHANGE,
                f"Report #{report.id} status updated",
                body,
                report=report,
            ),
            call(
                recipient2,
                NotificationType.STATUS_CHANGE,
                f"Report #{report.id} status updated",
                body,
                report=report,
            ),
        ]
    )