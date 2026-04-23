from __future__ import annotations

from typing import TYPE_CHECKING

from participium.models.message import Message
from participium.models.enums import Role
from participium.models.report import Report
from participium.models.user import User
from participium.database.session import Session
from participium.repositories.message_repository import MessageRepository
from participium.repositories.report_repository import ReportRepository

if TYPE_CHECKING:
    from participium.services.notification_service import NotificationService


class MessagingService:
    def __init__(
        self,
        session: Session | None = None,
        report_repository: ReportRepository | None = None,
        message_repository: MessageRepository | None = None,
        notification_service: NotificationService | None = None,
    ):
        self.session = session
        self.report_repository = report_repository
        self.message_repository = message_repository
        self.notification_service = notification_service

    def send_message(self, report: Report, sender: User, body: str) -> Message:
        """Send a message inside a report conversation.

        Inputs:
            report: target report.
            sender: user sending the message.
            body: message body.

        Returns:
            The persisted `Message`.

        Raises:
            AuthorizationError: if `sender` cannot access the thread.
            ValidationError: if `body` is empty or blank after trimming.
            ValidationError: if no recipient can currently be resolved for the conversation.
        """
        raise NotImplementedError

    def _resolve_recipient(self, report: Report, sender: User) -> User | None:
        if sender.role in {Role.ADMIN, Role.OPERATOR}:
            return report.reporter
        messages = self.message_repository.list_for_report(report.id)
        for message in reversed(messages):
            if message.sender and message.sender.role in {Role.ADMIN, Role.OPERATOR}:
                return message.sender
        for status_event in reversed(report.status_history):
            if status_event.changed_by and status_event.changed_by.role in {Role.ADMIN, Role.OPERATOR}:
                return status_event.changed_by
        return None
