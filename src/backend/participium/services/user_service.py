from __future__ import annotations

from werkzeug.datastructures import FileStorage

from participium.core.exceptions import ValidationError
from participium.database.session import Session
from participium.models.enums import Role
from participium.models.user import User
from participium.repositories.category_repository import CategoryRepository
from participium.repositories.notification_repository import NotificationRepository
from participium.repositories.token_repository import TokenRepository
from participium.repositories.user_repository import UserRepository
from participium.services.storage_service import StorageService


class UserService:
    def __init__(
        self,
        session: Session | None = None,
        user_repository: UserRepository | None = None,
        category_repository: CategoryRepository | None = None,
        token_repository: TokenRepository | None = None,
        notification_repository: NotificationRepository | None = None,
        storage_service: StorageService | None = None,
    ):
        self.session = session
        self.user_repository = user_repository
        self.category_repository = category_repository
        self.token_repository = token_repository
        self.notification_repository = notification_repository
        self.storage_service = storage_service

    def get_user(self, user_id: int) -> User:
        raise NotImplementedError

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

    def update_user(self, user_id: int, payload: dict) -> User:
        user = self.get_user(user_id)
        username = payload.get("username")
        email = payload.get("email")
        if username and username != user.username and self.user_repository.get_by_username(username):
            raise ValidationError("Username already in use.")
        if email and email != user.email and self.user_repository.get_by_email(email):
            raise ValidationError("Email already in use.")
        for field in ["username", "first_name", "last_name", "email"]:
            if payload.get(field) is not None:
                value = payload[field]
                setattr(user, field, value.strip() if isinstance(value, str) else value)
        next_role = self._parse_role(payload["role"]) if payload.get("role") is not None else user.role
        if payload.get("role") is not None:
            user.role = next_role
        if "category_id" in payload or payload.get("role") is not None:
            category = self._resolve_operator_category(next_role, payload.get("category_id", user.category_id))
            user.category_id = category.id if category else None
        if payload.get("is_active") is not None:
            user.is_active = bool(payload["is_active"])
        if payload.get("email_notifications_enabled") is not None:
            user.email_notifications_enabled = bool(payload["email_notifications_enabled"])
        self.session.commit()
        return user

    @staticmethod
    def _parse_role(role_value: str) -> Role:
        raise NotImplementedError

    def _resolve_operator_category(self, role: Role, category_id_value) -> object | None:
        raise NotImplementedError
