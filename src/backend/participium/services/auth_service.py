from __future__ import annotations

from participium.models.user import User


class AuthService:
    def verify_email(self, token_value: str) -> User:
        """Verify a pending email-verification token.

        Inputs:
            token_value: verification token received by the user.

        Returns:
            The verified `User`.

        Raises:
            ValidationError: if the token does not exist.
            ValidationError: if the token was already used.
            ValidationError: if the token is expired.
        """
        raise NotImplementedError

    def authenticate(self, identifier: str, password: str) -> User:
        """Authenticate a user by username or email plus password.

        Inputs:
            identifier: username or email of the target user.
            password: plaintext password to verify.

        Returns:
            The authenticated `User`.

        Raises:
            AuthenticationError: if credentials are invalid.
            AuthenticationError: if the matched user exists but is inactive.
            AuthenticationError: if the matched user exists but email is not verified.
        """
        raise NotImplementedError
