from __future__ import annotations

from participium.models.message import Message


class MessageRepository:
    def list_for_report(self, report_id: int) -> list[Message]:
        raise NotImplementedError
