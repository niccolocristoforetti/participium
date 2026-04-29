from __future__ import annotations

import pytest
from unittest.mock import Mock, call

from participium.models.enums import NotificationType, Role
from participium.models.report import Report
from participium.models.user import User
from participium.services.notification_service import NotificationService


pytestmark = pytest.mark.whitebox


def _user(*, user_id: int, role: Role = Role.CITIZEN) -> User:
    return User(id=user_id, username=f"user{user_id}", role=role)


def _report(*, report_id: int) -> Report:
    return Report(id=report_id)


@pytest.fixture
def notification_service() -> NotificationService:
    service = NotificationService(
        session=Mock(),
        notification_repository=Mock(),
        email_gateway=Mock(),
    )
    service.create_notification = Mock()
    return service


def test_t1_notify_status_change_creates_notification_for_single_recipient(
    notification_service: NotificationService,
) -> None:
    """T1: un singolo destinatario"""
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


def test_t2_notify_status_change_skips_none_recipients(
    notification_service: NotificationService,
) -> None:
    """T2: recipient=None non entro nel ciclo"""
    service = notification_service
    report = _report(report_id=1)

    service.notify_status_change([None], report, "body" )

    service.create_notification.assert_not_called()


def test_t3_notify_status_change_skips_duplicate_recipient_ids(
    notification_service: NotificationService,
) -> None:
    """T3: due utenti con lo stesso id entro nel ciclo ma anche nel ramo true dell if"""
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


def test_t4_notify_status_change_handles_empty_recipient_list(
    notification_service: NotificationService,
) -> None:
    """T4: lista vuota di destinatari"""
    service = notification_service
    report = _report(report_id=13)

    service.notify_status_change([], report, "body")

    service.create_notification.assert_not_called()


def test_t5_notify_status_change_sends_notification_to_multiple_unique_recipients(
    notification_service: NotificationService,
) -> None:
    """T5: due destinatari distinti"""
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

