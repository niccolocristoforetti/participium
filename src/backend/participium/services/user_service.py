from __future__ import annotations

from werkzeug.datastructures import FileStorage

from participium.models.user import User


class UserService:
    def update_profile(
        self,
        user: User,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        email_notifications_enabled: bool | None = None,
        profile_picture: FileStorage | None = None,
    ) -> User:
        """Update editable fields of a user profile.

        Inputs:
            user: persisted user to update.
            username: optional new username.
            first_name: optional new first name.
            last_name: optional new last name.
            email_notifications_enabled: optional notification preference update.
            profile_picture: optional uploaded profile picture.

        Returns:
            The updated `User`.

        Raises:
            ValidationError: if `username` is already used by another account.
        """
        raise NotImplementedError
