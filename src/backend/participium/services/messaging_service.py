from __future__ import annotations

from participium.models.message import Message
from participium.models.report import Report
from participium.models.user import User


class MessagingService:
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
