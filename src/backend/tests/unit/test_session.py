from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.engine import Connection

from participium.database import session as session_module


pytestmark = pytest.mark.unit


class TestDatabaseUrlFromEnv:
    """Test per la funzione _database_url_from_env."""

    def test_database_url_from_env_returns_url_when_set(self, monkeypatch):
        """Test che ritorna il valore di DATABASE_URL quando impostato."""
        test_url = "mysql://user:pass@localhost/db"
        monkeypatch.setenv("DATABASE_URL", test_url)
        
        result = session_module._database_url_from_env()
        
        assert result == test_url

    def test_database_url_from_env_raises_error_when_not_set(self, monkeypatch):
        """Test che solleva RuntimeError quando DATABASE_URL non è impostato."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        
        with pytest.raises(RuntimeError, match="DATABASE_URL environment variable is required"):
            session_module._database_url_from_env()


class TestOpenConnection:
    """Test per la funzione open_connection."""

    def test_open_connection_creates_engine_and_connection(self, monkeypatch):
        """Test che open_connection crei un engine e ritorni una connessione."""
        test_url = "sqlite:///:memory:"
        monkeypatch.setenv("DATABASE_URL", test_url)
        
        # Mock close_connection per evitare effetti collaterali
        with patch.object(session_module, 'close_connection'):
            mock_engine = MagicMock()
            mock_connection = MagicMock(spec=Connection)
            mock_engine.connect.return_value = mock_connection
            
            with patch('participium.database.session.create_engine', return_value=mock_engine) as mock_create_engine:
                result = session_module.open_connection()
            
            mock_create_engine.assert_called_once_with(test_url, future=True)
            mock_engine.connect.assert_called_once()
            assert result == mock_connection

    def test_open_connection_configures_session_local(self, monkeypatch):
        """Test che open_connection configuri SessionLocal."""
        test_url = "sqlite:///:memory:"
        monkeypatch.setenv("DATABASE_URL", test_url)
        
        with patch.object(session_module, 'close_connection'):
            mock_engine = MagicMock()
            mock_connection = MagicMock(spec=Connection)
            mock_engine.connect.return_value = mock_connection
            
            with patch('participium.database.session.create_engine', return_value=mock_engine):
                with patch.object(session_module.SessionLocal, 'configure') as mock_configure:
                    session_module.open_connection()
                    
                    # Verifica che configure sia stato chiamato
                    assert mock_configure.called

    def test_open_connection_calls_close_connection_first(self, monkeypatch):
        """Test che open_connection chiami close_connection prima di aprire una nuova."""
        test_url = "sqlite:///:memory:"
        monkeypatch.setenv("DATABASE_URL", test_url)
        
        with patch.object(session_module, 'close_connection') as mock_close:
            mock_engine = MagicMock()
            mock_connection = MagicMock(spec=Connection)
            mock_engine.connect.return_value = mock_connection
            
            with patch('participium.database.session.create_engine', return_value=mock_engine):
                session_module.open_connection()
            
            mock_close.assert_called_once()


class TestCloseConnection:
    """Test per la funzione close_connection."""

    def test_close_connection_removes_session(self):
        """Test che close_connection rimuova la sessione."""
        with patch.object(session_module.SessionLocal, 'remove') as mock_remove:
            # Mock l'attributo globale _connection come None
            with patch.object(session_module, '_connection', None):
                session_module.close_connection()
            
            mock_remove.assert_called_once()

    def test_close_connection_closes_and_disposes_engine(self):
        """Test che close_connection chiuda e dispose l'engine."""
        mock_engine = MagicMock()
        mock_connection = MagicMock(spec=Connection)
        mock_connection.engine = mock_engine
        
        with patch.object(session_module.SessionLocal, 'remove'):
            with patch.object(session_module, '_connection', mock_connection):
                session_module.close_connection()
            
            mock_connection.close.assert_called_once()
            mock_engine.dispose.assert_called_once()

    def test_close_connection_configures_session_local_with_none(self):
        """Test che close_connection configuri SessionLocal con None."""
        with patch.object(session_module.SessionLocal, 'remove'):
            with patch.object(session_module, '_connection', None):
                with patch.object(session_module.SessionLocal, 'configure') as mock_configure:
                    session_module.close_connection()
                
                mock_configure.assert_called_with(bind=None)


class TestConfigureDatabase:
    """Test per la funzione configure_database."""

    def test_configure_database_returns_connection(self, monkeypatch):
        """Test che configure_database ritorni una connessione."""
        test_url = "sqlite:///:memory:"
        monkeypatch.setenv("DATABASE_URL", test_url)
        
        with patch.object(session_module, 'close_connection'):
            mock_engine = MagicMock()
            mock_connection = MagicMock(spec=Connection)
            mock_engine.connect.return_value = mock_connection
            
            with patch('participium.database.session.create_engine', return_value=mock_engine):
                result = session_module.configure_database()
            
            assert result == mock_connection


class TestGetSession:
    """Test per la funzione get_session."""

    def test_get_session_returns_session_from_session_local(self):
        """Test che get_session ritorni una sessione da SessionLocal."""
        mock_session = MagicMock()
        
        with patch('participium.database.session.SessionLocal', return_value=mock_session):
            result = session_module.get_session()
            
            assert result == mock_session


class TestRemoveSession:
    """Test per la funzione remove_session."""

    def test_remove_session_calls_session_local_remove(self):
        """Test che remove_session chiami SessionLocal.remove()."""
        with patch.object(session_module.SessionLocal, 'remove') as mock_remove:
            session_module.remove_session()
            
            mock_remove.assert_called_once()


class TestCreateAll:
    """Test per la funzione create_all."""

    def test_create_all_raises_error_when_connection_is_none(self):
        """Test che create_all sollevi RuntimeError quando _connection è None."""
        with patch.object(session_module, '_connection', None):
            with pytest.raises(RuntimeError, match="Database connection is not open"):
                session_module.create_all()

    def test_create_all_creates_tables_when_connection_exists(self):
        """Test che create_all crei tutte le tabelle quando la connessione esiste."""
        mock_engine = MagicMock()
        mock_connection = MagicMock(spec=Connection)
        mock_connection.engine = mock_engine
        
        with patch.object(session_module, '_connection', mock_connection):
            with patch.object(session_module.Base.metadata, 'create_all') as mock_create_all:
                session_module.create_all()
                
                mock_create_all.assert_called_once_with(bind=mock_connection)