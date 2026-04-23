from __future__ import annotations

from participium.models.token import EmailVerificationToken


class TokenRepository:
    def get_by_token(self, token: str) -> EmailVerificationToken | None:
        raise NotImplementedError

    def add(self, token: EmailVerificationToken) -> None:
        raise NotImplementedError
