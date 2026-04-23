from __future__ import annotations

from participium.database.session import Session
from participium.gateways.email_gateway import EmailGateway
from participium.models.enums import NotificationType
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User
from participium.repositories.notification_repository import NotificationRepository


class NotificationService:
    def __init__(
        self,
        session: Session | None = None,
        notification_repository: NotificationRepository | None = None,
        email_gateway: EmailGateway | None = None,
    ):
        self.session = session
        self.notification_repository = notification_repository
        self.email_gateway = email_gateway

    def create_notification(
        self,
        user: User | None,
        notification_type: NotificationType,
        title: str,
        body: str,
        report: Report | None = None,
    ) -> Notification | None:
        """Create a notification, optionally associated with a report.

        Inputs:
            user: recipient user, or `None`.
            notification_type: semantic notification kind.
            title: short notification title.
            body: notification message body.
            report: optional related report.

        Returns:
            A persisted `Notification` for a non-null user, otherwise `None`.

        Raises:
            No documented domain exception from the method contract itself.
            Email delivery failures, if any, are internally swallowed after logging.
        """
        raise NotImplementedError

    def notify_status_change(self, recipients: list[User | None], report: Report, body: str) -> None:
        seen = set()
        for recipient in recipients:
            if recipient is None or recipient.id in seen:
                continue
            seen.add(recipient.id)
            self.create_notification(
                recipient,
                NotificationType.STATUS_CHANGE,
                f"Report #{report.id} status updated",
                body,
                report=report,
            )

    def count_unread_message_notifications_by_report(self, user_id: int) -> dict[int, int]:
        notifications = self.notification_repository.list_unread_message_notifications(user_id=user_id)
        counts: dict[int, int] = {}
        for notification in notifications:
            if notification.report_id is None:
                continue
            counts[notification.report_id] = counts.get(notification.report_id, 0) + 1
        return counts

    def mark_report_message_notifications_as_read(self, user_id: int, report_id: int) -> int:
        notifications = self.notification_repository.list_unread_message_notifications(
            user_id=user_id,
            report_id=report_id,
        )
        for notification in notifications:
            notification.is_read = True
        if notifications:
            self.session.commit()
        return len(notifications)
