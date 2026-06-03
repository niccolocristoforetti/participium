
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


VALID_TOKEN   = "VALID_TOKEN_FOR_MARIA_ROSSI"
USED_TOKEN    = "USED_TOKEN_FOR_LUCA_BIANCHI"
INVALID_TOKEN = "INVALID_TOKEN"
EXPIRED_TOKEN = "EXPIRED_TOKEN_FOR_GIULIA_NERI"


@pytest.fixture
def seed_verify_email_data():
    """
    Crea un DB SQLite in-memory con:
    - Utente id=101  (maria.rossi,  is_email_verified=False, token valido)
    - Utente id=102  (luca.bianchi, is_email_verified=True,  token già usato)
    - Utente id=103  (giulia.neri,  is_email_verified=False, token scaduto)
    Restituisce un AuthService pronto all'uso.
    """
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



#  token valido → utente verificato
# VE1 – token valido, utente non ancora verificato
def test_ve1_valid_token(seed_verify_email_data) -> None:
    result = seed_verify_email_data.verify_email(VALID_TOKEN)

    assert isinstance(result, User)
    assert result.id == 101
    assert result.username == "maria.rossi"
    assert result.first_name == "Maria"
    assert result.last_name == "Rossi"
    assert result.email == "maria.rossi@example.com"
    assert result.is_email_verified is True


#token non valido → ValidationError

@pytest.mark.parametrize(
    "token",
    [
        # VE2 – token già utilizzato
        USED_TOKEN,
        # VE3 – token inesistente
        INVALID_TOKEN,
        # VE4 – token scaduto
        EXPIRED_TOKEN,
    ],
)
def test_ve_invalid_token(seed_verify_email_data, token) -> None:
    with pytest.raises(ValidationError):
        seed_verify_email_data.verify_email(token)