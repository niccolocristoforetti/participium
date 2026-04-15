from __future__ import annotations

from participium.models.enums import NotificationType
from participium.models.notification import Notification
from participium.models.report import Report
from participium.models.user import User


class NotificationService:
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
