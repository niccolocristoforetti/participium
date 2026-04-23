from __future__ import annotations

from participium.models.user import User


class UserRepository:
    def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError
