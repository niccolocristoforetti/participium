#aaaaaaaaaaaaa
import pytest
from participium.database import close_connection, create_all, get_session, open_connection
from participium.repositories.category_repository import CategoryRepository
from participium.repositories.message_repository import MessageRepository
from participium.repositories.notification_repository import NotificationRepository
from participium.repositories.report_repository import ReportRepository
from participium.repositories.token_repository import TokenRepository
from participium.repositories.user_repository import UserRepository


@pytest.fixture(scope="function")
def db_session(monkeypatch):
    """
    Fixture che prepara un database in memoria SQLite per ogni singolo test.
    Ogni test ottiene un database completamente isolato e pulito: nessun dato
    residuo da altri test può influenzare i risultati.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    open_connection()
    create_all()
    session = get_session()

    yield session

    close_connection()


# ---------------------------------------------------------------------------
# Fixture dei repository centralizzate qui per evitare duplicazione nei file
# di test. Lo scope è dichiarato esplicitamente per leggibilità e per evitare
# sorprese in caso di future modifiche allo scope di db_session.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def category_repository(db_session):
    return CategoryRepository(db_session)


@pytest.fixture(scope="function")
def message_repository(db_session):
    return MessageRepository(db_session)


@pytest.fixture(scope="function")
def notification_repository(db_session):
    return NotificationRepository(db_session)


@pytest.fixture(scope="function")
def report_repository(db_session):
    return ReportRepository(db_session)


@pytest.fixture(scope="function")
def token_repository(db_session):
    return TokenRepository(db_session)


@pytest.fixture(scope="function")
def user_repository(db_session):
    return UserRepository(db_session)