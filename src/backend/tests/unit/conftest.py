from __future__ import annotations

from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from participium.models.base import Base
from participium.services.auth_service import AuthService
from participium.services.category_service import CategoryService


@pytest.fixture
def in_memory_session():
    """
    Fixture per creare una sessione SQLAlchemy in-memory per test unitari.
    
    Crea un database SQLite in-memoria, prepara tutte le tabelle,
    e le ripulisce dopo il test.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)

    session = SessionLocal()
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


# ====== Fixtures for AuthService ======

@pytest.fixture
def mock_session():
    """Mock della sessione SQLAlchemy."""
    return Mock()


@pytest.fixture
def mock_user_repository():
    """Mock del repository degli utenti."""
    return Mock()


@pytest.fixture
def mock_token_repository():
    """Mock del repository dei token."""
    return Mock()


@pytest.fixture
def mock_email_gateway():
    """Mock del gateway per l'invio email."""
    return Mock()


@pytest.fixture
def auth_service(mock_session, mock_user_repository, mock_token_repository, mock_email_gateway):
    """Fixture per istanziare AuthService con mock delle dipendenze."""
    return AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        token_repository=mock_token_repository,
        email_gateway=mock_email_gateway,
    )


# ====== Fixtures for CategoryService ======

@pytest.fixture
def mock_category_repository():
    """Mock del repository delle categorie."""
    return Mock()


@pytest.fixture
def category_service(mock_session, mock_category_repository):
    """Fixture per istanziare CategoryService con mock delle dipendenze."""
    return CategoryService(
        session=mock_session,
        category_repository=mock_category_repository,
    )
