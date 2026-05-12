from __future__ import annotations

from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from participium.models.base import Base
from participium.services.auth_service import AuthService
from participium.services.category_service import CategoryService
from participium.services.messaging_service import MessagingService
from participium.services.notification_service import NotificationService
from participium.services.report_service import ReportService
from participium.services.statistics_service import StatisticsService
from participium.services.user_service import UserService


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


# ====== Fixtures for UserService ======

@pytest.fixture
def mock_notification_repository():
    """Mock del repository delle notifiche."""
    return Mock()


@pytest.fixture
def mock_report_repository():
    """Mock del repository dei report."""
    return Mock()


@pytest.fixture
def mock_message_repository():
    """Mock del repository dei messaggi."""
    return Mock()


@pytest.fixture
def mock_storage_service():
    """Mock del servizio di storage."""
    return Mock()


@pytest.fixture
def user_service(
    mock_session, mock_user_repository, mock_category_repository,
    mock_token_repository, mock_notification_repository, mock_storage_service,
):
    """Fixture per istanziare UserService con mock delle dipendenze."""
    return UserService(
        session=mock_session,
        user_repository=mock_user_repository,
        category_repository=mock_category_repository,
        token_repository=mock_token_repository,
        notification_repository=mock_notification_repository,
        storage_service=mock_storage_service,
    )


# ====== Fixtures for NotificationService ======

@pytest.fixture
def notification_service(mock_session, mock_notification_repository, mock_email_gateway):
    """Fixture per istanziare NotificationService con mock delle dipendenze."""
    return NotificationService(
        session=mock_session,
        notification_repository=mock_notification_repository,
        email_gateway=mock_email_gateway,
    )


# ====== Fixtures for MessagingService ======

@pytest.fixture
def mock_notification_service():
    """Mock del servizio di notifica."""
    return Mock()


@pytest.fixture
def messaging_service(
    mock_session, mock_report_repository, mock_message_repository, mock_notification_service,
):
    """Fixture per istanziare MessagingService con mock delle dipendenze."""
    return MessagingService(
        session=mock_session,
        report_repository=mock_report_repository,
        message_repository=mock_message_repository,
        notification_service=mock_notification_service,
    )


# ====== Fixtures for ReportService ======

@pytest.fixture
def report_service(
    mock_session, mock_report_repository, mock_category_repository,
    mock_storage_service, mock_notification_service,
):
    """Fixture per istanziare ReportService con mock delle dipendenze."""
    return ReportService(
        session=mock_session,
        report_repository=mock_report_repository,
        category_repository=mock_category_repository,
        storage_service=mock_storage_service,
        notification_service=mock_notification_service,
    )


# ====== Fixtures for StatisticsService ======

@pytest.fixture
def statistics_service(mock_report_repository):
    """Fixture per istanziare StatisticsService con mock delle dipendenze."""
    return StatisticsService(
        report_repository=mock_report_repository,
    )
