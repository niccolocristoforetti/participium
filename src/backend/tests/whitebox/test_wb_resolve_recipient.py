from __future__ import annotations

from unittest.mock import Mock
import pytest

from participium.models.enums import Role
from participium.models.message import Message
from participium.models.report import Report, ReportStatusHistory
from participium.models.user import User
from participium.services.messaging_service import MessagingService


pytestmark = pytest.mark.whitebox



#  Helpers 


# crea un'istanza mock di un utente con un id e un ruolo specifici.
def _user(*, user_id: int, role: Role) -> User:
    return User(id=user_id, role=role)


# crea un'istanza mock di un messaggio inviato da un determinato utente.
def _message(*, sender: User | None) -> Message:
    return Message(sender=sender)


# crea un evento di cronologia di stato modificato da un determinato utente.
def _status_event(*, changed_by: User | None) -> ReportStatusHistory:
    return ReportStatusHistory(changed_by=changed_by)


# configura un report mock completo di segnalatore e cronologia degli stati.
def _report(
    *,
    reporter: User | None = None,
    status_history: list[ReportStatusHistory] | None = None,
) -> Report:
    return Report(id=1, reporter=reporter, status_history=status_history or [])



#  Fixtures 


# Inizializza MessagingService isolando il modulo e mockando la repository dei messaggi.
@pytest.fixture
def service() -> MessagingService:
    return MessagingService(session=Mock(), message_repository=Mock())



#  Casi di Test 


# RR1 – ADMIN: verifica che se il mittente è un amministratore o operatore, venga restituito direttamente l'autore della segnalazione.
def test_rr1_sender_is_admin_returns_reporter(service: MessagingService) -> None:
    reporter = _user(user_id=10, role=Role.CITIZEN)
    report = _report(reporter=reporter)
    sender = _user(user_id=1, role=Role.ADMIN)

    result = service._resolve_recipient(report, sender)

    assert result is reporter
    service.message_repository.list_for_report.assert_not_called()


# RR2 – verifica che venga estratto l'ultimo mittente ADMIN/OPERATOR scorrendo a ritroso la lista dei messaggi.
def test_rr2_message_with_admin_sender_returns_message_sender(service: MessagingService) -> None:
    admin = _user(user_id=2, role=Role.ADMIN)
    msg = _message(sender=admin)
    service.message_repository.list_for_report.return_value = [msg]
    report = _report()
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is admin


# RR3 – verifica che, in assenza di messaggi validi, venga estratto l'ultimo amministratore dalla cronologia degli stati.
def test_rr3_status_event_with_admin_changed_by_returns_changed_by(service: MessagingService) -> None:
    admin = _user(user_id=3, role=Role.ADMIN)
    service.message_repository.list_for_report.return_value = []
    report = _report(status_history=[_status_event(changed_by=admin)])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is admin


# RRB1 – verifica che se non ci sono messaggi né cronologia degli stati, la funzione restituisca None.
def test_rrb1_no_messages_no_status_returns_none(service: MessagingService) -> None:
    service.message_repository.list_for_report.return_value = []
    report = _report(status_history=[])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is None


# RR4 – verifica che se messaggi e stati appartengono solo a cittadini ordinari, non venga rilevato alcun destinatario (restituisce None).
def test_rr4_non_admin_message_and_status_returns_none(service: MessagingService) -> None:
    citizen = _user(user_id=5, role=Role.CITIZEN)
    service.message_repository.list_for_report.return_value = [_message(sender=citizen)]
    report = _report(status_history=[_status_event(changed_by=citizen)])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is None


# RR5 – verifica il corretto superamento dei rami logici nel caso in cui il mittente del messaggio o l'autore dello stato siano None.
def test_rr5_message_sender_none_and_changed_by_none_returns_none(service: MessagingService) -> None:
    service.message_repository.list_for_report.return_value = [_message(sender=None)]
    report = _report(status_history=[_status_event(changed_by=None)])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is None


# RR6 – verifica che l'intero overflow di messaggi e stati non autorizzati venga processato scorrendo tutti gli elementi senza match.
def test_rr6_multiple_non_admin_messages_and_statuses_returns_none(service: MessagingService) -> None:
    citizen = _user(user_id=7, role=Role.CITIZEN)
    service.message_repository.list_for_report.return_value = [
        _message(sender=citizen),
        _message(sender=citizen),
    ]
    report = _report(
        status_history=[
            _status_event(changed_by=citizen),
            _status_event(changed_by=citizen),
        ]
    )
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is None