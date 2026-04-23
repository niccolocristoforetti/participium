from __future__ import annotations

from participium.models.notification import Notification


class NotificationRepository:
    def add(self, notification: Notification) -> None:
        raise NotImplementedError

    def list_unread_message_notifications(
        self,
        user_id: int,
        report_id: int | None = None,
    ) -> list[Notification]:
        raise NotImplementedError
