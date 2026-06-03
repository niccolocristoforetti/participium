from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from participium.container import AppContainer, ControllerBundle, get_controllers
from participium.controllers import (
    AdminController,
    AuthController,
    OperatorController,
    ReportController,
    StatisticsController,
    UserController,
    
)
from participium.models.base import Base
from participium.repositories import (
    CategoryRepository,
    MessageRepository,
    NotificationRepository,
    ReportRepository,
    TokenRepository,
    UserRepository,
)
from participium.services import (
    AuthService,
    CategoryService,
    LocalFileStorageService,
    MessagingService,
    NotificationService,
    ReportService,
    StatisticsService,
    UserService,
)
from participium.services.email_service import ConsoleEmailGateway


@pytest.fixture
def tmp_settings(tmp_path):
    """
    Crea un Settings minimale in-memory per i test di integrazione:
    - mail_backend="console" → ConsoleEmailGateway, nessuna connessione SMTP
    - media_root e mail_outbox_dir su tmp_path → nessuna scrittura in src tree
    - tutti gli altri campi con valori di default sicuri
    """
    from participium.config.settings import Settings

    return Settings(
        app_name="participium-test",
        secret_key="test-secret",
        debug=True,
        frontend_origin="http://localhost:5173",
        host="127.0.0.1",
        port=5050,
        auto_init_db=False,
        bootstrap_reference_data=False,
        bootstrap_demo_data=False,
        mail_backend="console",
        mail_from="noreply@test.local",
        mail_outbox_dir=tmp_path / "outbox",
        smtp_host=None,
        smtp_port=587,
        smtp_username=None,
        smtp_password=None,
        smtp_use_tls=False,
        expose_verification_links=False,
        media_root=tmp_path / "uploads",
        max_content_length=16 * 1024 * 1024,
        instance_path=tmp_path / "instance",
    )


@pytest.fixture
def db_session_for_container():
    """
    Crea una sessione SQLite in-memory isolata da iniettare nel container,
    sostituendo la scoped_session globale di get_session().
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def container(tmp_settings):
    return AppContainer(tmp_settings)


@pytest.fixture
def bundle(container, db_session_for_container):
    """
    Costruisce il ControllerBundle patchando get_session() con la sessione
    in-memory, in modo che tutti i repository e service usino lo stesso DB isolato.
    """
    with patch(
        "participium.container.get_session",
        return_value=db_session_for_container,
    ):
        yield container.build_controllers()



# Inizializzazione del container


# CT1 – AppContainer si inizializza con settings validi
def test_ct1_container_init(container, tmp_settings) -> None:
    assert isinstance(container.settings, type(tmp_settings))
    assert container.settings.media_root == tmp_settings.media_root


# CT2 – mail_backend="console" → email_gateway è ConsoleEmailGateway
def test_ct2_email_gateway_is_console(container) -> None:
    assert isinstance(container.email_gateway, ConsoleEmailGateway)


# CT3 – storage_service è LocalFileStorageService
def test_ct3_storage_service_type(container) -> None:
    assert isinstance(container.storage_service, LocalFileStorageService)


# CT4 – storage_service usa il media_root del settings
def test_ct4_storage_service_media_root(container, tmp_settings) -> None:
    assert Path(container.storage_service.media_root) == Path(tmp_settings.media_root)



# Tipo e struttura del ControllerBundle


# CT5 – build_controllers() restituisce un ControllerBundle
def test_ct5_bundle_type(bundle) -> None:
    assert isinstance(bundle, ControllerBundle)


# CT6 – tutti i controller hanno il tipo corretto
@pytest.mark.parametrize(
    "attr, expected_type",
    [
        # CT6a – AuthController
        ("auth", AuthController),
        # CT6b – UserController
        ("users", UserController),
        # CT6c – ReportController
        ("reports", ReportController),
        # CT6d – OperatorController
        ("operators", OperatorController),
        # CT6e – AdminController
        ("admin", AdminController),
        # CT6f – StatisticsController
        ("statistics", StatisticsController),
    ],
)
def test_ct6_controller_types(bundle, attr, expected_type) -> None:
    assert isinstance(getattr(bundle, attr), expected_type)


# CT7 – repositories contiene esattamente le sei chiavi attese
def test_ct7_repositories_keys(bundle) -> None:
    assert set(bundle.repositories.keys()) == {
        "users", "categories", "reports", "messages", "notifications", "tokens",
    }


# CT8 – ogni repository ha il tipo corretto
@pytest.mark.parametrize(
    "key, expected_type",
    [
        # CT8a – UserRepository
        ("users", UserRepository),
        # CT8b – CategoryRepository
        ("categories", CategoryRepository),
        # CT8c – ReportRepository
        ("reports", ReportRepository),
        # CT8d – MessageRepository
        ("messages", MessageRepository),
        # CT8e – NotificationRepository
        ("notifications", NotificationRepository),
        # CT8f – TokenRepository
        ("tokens", TokenRepository),
    ],
)
def test_ct8_repository_types(bundle, key, expected_type) -> None:
    assert isinstance(bundle.repositories[key], expected_type)



# Cablaggio service -> controller 


# CT9 – AuthController riceve un AuthService
def test_ct9_auth_controller_wiring(bundle) -> None:
    assert isinstance(bundle.auth.auth_service, AuthService)


# CT10 – UserController riceve un UserService e un NotificationService
def test_ct10_user_controller_wiring(bundle) -> None:
    assert isinstance(bundle.users.user_service, UserService)
    assert isinstance(bundle.users.notification_service, NotificationService)


# CT11 – ReportController riceve ReportService, MessagingService, NotificationService
def test_ct11_report_controller_wiring(bundle) -> None:
    assert isinstance(bundle.reports.report_service, ReportService)
    assert isinstance(bundle.reports.messaging_service, MessagingService)
    assert isinstance(bundle.reports.notification_service, NotificationService)


# CT12 – OperatorController riceve ReportService e NotificationService
def test_ct12_operator_controller_wiring(bundle) -> None:
    assert isinstance(bundle.operators.report_service, ReportService)
    assert isinstance(bundle.operators.notification_service, NotificationService)


# CT13 – AdminController riceve CategoryService, UserService e StatisticsService
def test_ct13_admin_controller_wiring(bundle) -> None:
    assert isinstance(bundle.admin.category_service, CategoryService)
    assert isinstance(bundle.admin.user_service, UserService)
    assert isinstance(bundle.admin.statistics_service, StatisticsService)


# CT14 – StatisticsController riceve un StatisticsService
def test_ct14_statistics_controller_wiring(bundle) -> None:
    assert isinstance(bundle.statistics.statistics_service, StatisticsService)



# build_controllers() chiamate multiple restituiscono bundle distinti


# CT15 – due chiamate a build_controllers() producono bundle indipendenti
def test_ct15_bundle_isolation(container, db_session_for_container) -> None:
    with patch(
        "participium.container.get_session",
        return_value=db_session_for_container,
    ):
        bundle_a = container.build_controllers()
        bundle_b = container.build_controllers()

    assert bundle_a is not bundle_b
    assert bundle_a.auth is not bundle_b.auth

#CT16 – Verifica il recupero del container tramite l'estensione current_app di Flask
def test_ct16_current_app_container_extension(container, db_session_for_container) -> None:
    mock_app = MagicMock()
    mock_app.extensions = {"container": container}
    with patch("participium.container.current_app", mock_app), \
         patch("participium.container.get_session", return_value=db_session_for_container):
        result = get_controllers()
        assert isinstance(result, ControllerBundle)