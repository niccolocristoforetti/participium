from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from participium.core.exceptions import AuthenticationError
from participium.core.security import hash_password
from participium.models.base import Base
from participium.models.enums import Role
from participium.models.user import User
from participium.repositories.token_repository import TokenRepository
from participium.repositories.user_repository import UserRepository
from participium.services.auth_service import AuthService


CORRECT_PASSWORD = "correct_password"
WRONG_PASSWORD = "wrong_password"


@pytest.fixture
def seed_authenticate_data():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        active_user = User(
            username="mario.rossi",
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            password_hash=hash_password(CORRECT_PASSWORD),
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
            email_notifications_enabled=True,
        )
        inactive_user = User(
            username="inactive.user",
            first_name="Inactive",
            last_name="User",
            email="inactive.user@example.com",
            password_hash=hash_password(CORRECT_PASSWORD),
            role=Role.CITIZEN,
            is_active=False,
            is_email_verified=True,
            email_notifications_enabled=True,
        )
        unverified_user = User(
            username="unverified.user",
            first_name="Unverified",
            last_name="User",
            email="unverified.user@example.com",
            password_hash=hash_password(CORRECT_PASSWORD),
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=False,
            email_notifications_enabled=True,
        )
        session.add_all([active_user, inactive_user, unverified_user])
        session.commit()

        service = AuthService(
            session=session,
            user_repository=UserRepository(session),
            token_repository=TokenRepository(session),
            email_gateway=None,
        )

        yield service


def test_auth1_valid_username(seed_authenticate_data) -> None:
    user = seed_authenticate_data.authenticate("mario.rossi", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.username == "mario.rossi"


def test_auth2_valid_email(seed_authenticate_data) -> None:
    user = seed_authenticate_data.authenticate("mario.rossi@example.com", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.email == "mario.rossi@example.com"


def test_auth3_unknown_username(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("unknown_user", "any_password")


def test_auth4_unknown_email(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("unknown_user@example.com", "any_password")


def test_auth5_wrong_password_username(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("mario.rossi", WRONG_PASSWORD)


def test_auth6_wrong_password_email(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("mario.rossi@example.com", WRONG_PASSWORD)


def test_auth7_inactive_user_username(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("inactive.user", CORRECT_PASSWORD)


def test_auth8_inactive_user_email(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("inactive.user@example.com", CORRECT_PASSWORD)


def test_auth9_unverified_email_by_email(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("unverified.user@example.com", CORRECT_PASSWORD)


def test_auth10_unverified_email_by_username(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("unverified.user", CORRECT_PASSWORD)


def test_auth11_empty_identifier(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("", "any_password")


def test_auth12_empty_password_username(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("mario.rossi", "")


def test_auth13_empty_password_email(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("mario.rossi@example.com", "")


def test_auth14_both_empty(seed_authenticate_data) -> None:
    with pytest.raises(AuthenticationError):
        seed_authenticate_data.authenticate("", "")


def test_auth15_email_with_leading_trailing_spaces(seed_authenticate_data) -> None:
    user = seed_authenticate_data.authenticate(" mario.rossi@example.com ", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.email == "mario.rossi@example.com"


@pytest.mark.xfail(strict=True, reason="Email lookup is case-sensitive: uppercase chars in identifier are not normalized before the DB query.")
def test_auth16_email_with_uppercase_chars(seed_authenticate_data) -> None:
    user = seed_authenticate_data.authenticate("Mario.Rossi@Example.Com", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.email == "mario.rossi@example.com"


def test_auth17_username_with_leading_trailing_spaces(seed_authenticate_data) -> None:
    user = seed_authenticate_data.authenticate(" mario.rossi ", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.username == "mario.rossi"
