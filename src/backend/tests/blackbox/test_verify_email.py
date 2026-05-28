from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from participium.core.exceptions import ValidationError
from participium.core.utils import utcnow
from participium.models.base import Base
from participium.models.enums import Role
from participium.models.token import EmailVerificationToken
from participium.models.user import User
from participium.repositories.token_repository import TokenRepository
from participium.repositories.user_repository import UserRepository
from participium.services.auth_service import AuthService


VALID_TOKEN = "VALID_TOKEN_FOR_MARIA_ROSSI"
USED_TOKEN = "USED_TOKEN_FOR_LUCA_BIANCHI"
INVALID_TOKEN = "INVALID_TOKEN"
EXPIRED_TOKEN = "EXPIRED_TOKEN_FOR_GIULIA_NERI"


@pytest.fixture
def seed_verify_email_data():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user_pending = User(
            id=101,
            username="maria.rossi",
            first_name="Maria",
            last_name="Rossi",
            email="maria.rossi@example.com",
            password_hash="HASHED_PASSWORD_101",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=False,
            email_notifications_enabled=True,
        )
        user_used = User(
            id=102,
            username="luca.bianchi",
            first_name="Luca",
            last_name="Bianchi",
            email="luca.bianchi@example.com",
            password_hash="HASHED_PASSWORD_102",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
            email_notifications_enabled=True,
        )
        user_expired = User(
            id=103,
            username="giulia.neri",
            first_name="Giulia",
            last_name="Neri",
            email="giulia.neri@example.com",
            password_hash="HASHED_PASSWORD_103",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=False,
            email_notifications_enabled=True,
        )
        session.add_all([user_pending, user_used, user_expired])
        session.flush()

        session.add_all([
            EmailVerificationToken(
                user_id=user_pending.id,
                token=VALID_TOKEN,
                expires_at=utcnow() + timedelta(hours=48),
                is_used=False,
            ),
            EmailVerificationToken(
                user_id=user_used.id,
                token=USED_TOKEN,
                expires_at=utcnow() + timedelta(hours=48),
                is_used=True,
            ),
            EmailVerificationToken(
                user_id=user_expired.id,
                token=EXPIRED_TOKEN,
                expires_at=utcnow() - timedelta(hours=1),
                is_used=False,
            ),
        ])
        session.commit()

        yield AuthService(
            session=session,
            user_repository=UserRepository(session),
            token_repository=TokenRepository(session),
            email_gateway=None,
        )


def test_verify_email_success(seed_verify_email_data) -> None:
    verified_user = seed_verify_email_data.verify_email(VALID_TOKEN)

    assert isinstance(verified_user, User)
    assert verified_user.id == 101
    assert verified_user.username == "maria.rossi"
    assert verified_user.first_name == "Maria"
    assert verified_user.last_name == "Rossi"
    assert verified_user.email == "maria.rossi@example.com"
    assert verified_user.is_email_verified is True


def test_verify_email_used_token(seed_verify_email_data) -> None:
    with pytest.raises(ValidationError):
        seed_verify_email_data.verify_email(USED_TOKEN)


def test_verify_email_invalid_token(seed_verify_email_data) -> None:
    with pytest.raises(ValidationError):
        seed_verify_email_data.verify_email(INVALID_TOKEN)


def test_verify_email_expired_token(seed_verify_email_data) -> None:
    with pytest.raises(ValidationError):
        seed_verify_email_data.verify_email(EXPIRED_TOKEN)