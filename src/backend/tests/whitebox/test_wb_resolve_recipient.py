from __future__ import annotations

from unittest.mock import Mock

import pytest

from participium.models.enums import Role
from participium.models.message import Message
from participium.models.report import Report, ReportStatusHistory
from participium.models.user import User
from participium.services.messaging_service import MessagingService


pytestmark = pytest.mark.whitebox


def _user(*, user_id: int, role: Role) -> User:
    return User(id=user_id, role=role)


def _message(*, sender: User | None) -> Message:
    return Message(sender=sender)


def _status_event(*, changed_by: User | None) -> ReportStatusHistory:
    return ReportStatusHistory(changed_by=changed_by)


def _report(
    *,
    reporter: User | None = None,
    status_history: list[ReportStatusHistory] | None = None,
) -> Report:
    return Report(id=1, reporter=reporter, status_history=status_history or [])


@pytest.fixture
def service() -> MessagingService:
    return MessagingService(session=Mock(), message_repository=Mock())


# T1 — C1=True: sender is ADMIN → return report.reporter (Path P1)
def test_t1_sender_is_admin_returns_reporter(service: MessagingService) -> None:
    reporter = _user(user_id=10, role=Role.CITIZEN)
    report = _report(reporter=reporter)
    sender = _user(user_id=1, role=Role.ADMIN)

    result = service._resolve_recipient(report, sender)

    assert result is reporter
    service.message_repository.list_for_report.assert_not_called()


# T2 — Loop1=1 early return: first message has ADMIN sender (Path P3, Node/Edge/Condition C2a=T C2b=T)
def test_t2_message_with_admin_sender_returns_message_sender(service: MessagingService) -> None:
    admin = _user(user_id=2, role=Role.ADMIN)
    msg = _message(sender=admin)
    service.message_repository.list_for_report.return_value = [msg]
    report = _report()
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is admin


# T3 — Loop1=0, Loop2=1 early return: no messages, first status event has ADMIN changed_by (Path P4, C3a=T C3b=T)
def test_t3_status_event_with_admin_changed_by_returns_changed_by(service: MessagingService) -> None:
    admin = _user(user_id=3, role=Role.ADMIN)
    service.message_repository.list_for_report.return_value = []
    report = _report(status_history=[_status_event(changed_by=admin)])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is admin


# T4 — Loop1=0, Loop2=0: empty messages and empty status_history → return None (Path P2)
def test_t4_no_messages_no_status_returns_none(service: MessagingService) -> None:
    service.message_repository.list_for_report.return_value = []
    report = _report(status_history=[])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is None


# T5 — back-edges both loops exhausted: non-ADMIN message and non-ADMIN status event → return None
# (Path P5, Edge back-edges L1/L2, Condition C2b=F C3b=F)
def test_t5_non_admin_message_and_status_returns_none(service: MessagingService) -> None:
    citizen = _user(user_id=5, role=Role.CITIZEN)
    service.message_repository.list_for_report.return_value = [_message(sender=citizen)]
    report = _report(status_history=[_status_event(changed_by=citizen)])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is None


# T6 — C2a=False and C3a=False: message.sender is None and status_event.changed_by is None → return None
def test_t6_message_sender_none_and_changed_by_none_returns_none(service: MessagingService) -> None:
    service.message_repository.list_for_report.return_value = [_message(sender=None)]
    report = _report(status_history=[_status_event(changed_by=None)])
    sender = _user(user_id=99, role=Role.CITIZEN)

    result = service._resolve_recipient(report, sender)

    assert result is None


# T7 — Loop1=2+, Loop2=2+: multiple non-ADMIN messages and status events → return None
def test_t7_multiple_non_admin_messages_and_statuses_returns_none(service: MessagingService) -> None:
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
