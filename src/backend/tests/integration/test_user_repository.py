"""
Test di integrazione per UserRepository.

Copertura al 100% dei metodi pubblici:
  - add()
  - get_by_id()                — trovato, non trovato
  - get_by_email()             — trovato, non trovato
  - get_by_username()          — trovato, non trovato
  - get_by_username_or_email() — trovato per username, per email, non trovato
  - list_all()                 — ordinamento DESC per created_at
  - delete()

La fixture user_repository è definita in conftest.py.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.enums import Role
from participium.models.user import User


# Helper per costruire un utente con i campi obbligatori
def _make_user(username: str, email: str, **kwargs) -> User:
    return User(
        username=username,
        first_name=kwargs.pop("first_name", "Nome"),
        last_name=kwargs.pop("last_name", "Cognome"),
        email=email,
        password_hash=kwargs.pop("password_hash", "fakehash"),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# ADD / GET_BY_ID
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_user_and_get_by_id(user_repository, db_session):
    """add() persiste l'utente; get_by_id() lo recupera correttamente."""
    # Arrange
    user = _make_user(
        username="mario.rossi",
        email="mario@example.com",
        first_name="Mario",
        last_name="Rossi",
        role=Role.CITIZEN,
    )

    # Act
    added = user_repository.add(user)
    db_session.commit()

    # Assert
    assert added.id is not None
    fetched = user_repository.get_by_id(added.id)
    assert fetched is not None
    assert fetched.username == "mario.rossi"


@pytest.mark.integration
def test_get_by_id_returns_none_for_missing_user(user_repository):
    """get_by_id() restituisce None per un id inesistente."""
    assert user_repository.get_by_id(999) is None


# ---------------------------------------------------------------------------
# GET_BY_EMAIL
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_email_found(user_repository, db_session):
    """get_by_email() restituisce l'utente con quell'indirizzo email."""
    user = _make_user(username="luigi.verdi", email="luigi@example.com")
    user_repository.add(user)
    db_session.commit()

    result = user_repository.get_by_email("luigi@example.com")
    assert result is not None
    assert result.username == "luigi.verdi"


@pytest.mark.integration
def test_get_by_email_returns_none_when_not_found(user_repository):
    """get_by_email() restituisce None per un'email inesistente."""
    assert user_repository.get_by_email("nobody@example.com") is None


# ---------------------------------------------------------------------------
# GET_BY_USERNAME
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_username_found(user_repository, db_session):
    """get_by_username() restituisce l'utente con quel nome utente."""
    user = _make_user(username="giulia.bianchi", email="giulia@example.com")
    user_repository.add(user)
    db_session.commit()

    result = user_repository.get_by_username("giulia.bianchi")
    assert result is not None
    assert result.email == "giulia@example.com"


@pytest.mark.integration
def test_get_by_username_returns_none_when_not_found(user_repository):
    """get_by_username() restituisce None per uno username inesistente."""
    assert user_repository.get_by_username("nessuno") is None


# ---------------------------------------------------------------------------
# GET_BY_USERNAME_OR_EMAIL
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_username_or_email_by_username(user_repository, db_session):
    """get_by_username_or_email() trova l'utente cercando per username."""
    user = _make_user(username="utente1", email="utente1@example.com")
    user_repository.add(user)
    db_session.commit()

    result = user_repository.get_by_username_or_email("utente1")
    assert result is not None
    assert result.email == "utente1@example.com"


@pytest.mark.integration
def test_get_by_username_or_email_by_email(user_repository, db_session):
    """get_by_username_or_email() trova l'utente cercando per email."""
    user = _make_user(username="utente2", email="utente2@example.com")
    user_repository.add(user)
    db_session.commit()

    result = user_repository.get_by_username_or_email("utente2@example.com")
    assert result is not None
    assert result.username == "utente2"


@pytest.mark.integration
def test_get_by_username_or_email_returns_none_when_not_found(user_repository):
    """get_by_username_or_email() restituisce None se né username né email corrispondono."""
    assert user_repository.get_by_username_or_email("inesistente") is None


# ---------------------------------------------------------------------------
# LIST_ALL — ordine DESC per created_at
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_all_returns_all_users_sorted_by_created_at_desc(user_repository, db_session):
    """list_all() restituisce tutti gli utenti ordinati dal più recente al più vecchio.

    I created_at vengono impostati esplicitamente per garantire un ordine
    deterministico indipendente dalla velocità di SQLite in memoria.
    """
    now = datetime.now()
    u_old = _make_user(username="user_old", email="old@test.com",
                       created_at=now - timedelta(seconds=2))
    u_new = _make_user(username="user_new", email="new@test.com",
                       created_at=now)

    user_repository.add(u_old)
    user_repository.add(u_new)
    db_session.commit()

    results = user_repository.list_all()

    assert len(results) == 2
    assert results[0].username == "user_new"  # più recente per primo (DESC)
    assert results[1].username == "user_old"


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_delete_removes_user_from_database(user_repository, db_session):
    """delete() rimuove l'utente: non è più recuperabile dopo il commit."""
    u1 = _make_user(username="user_a", email="a@test.com")
    u2 = _make_user(username="user_b", email="b@test.com")
    user_repository.add(u1)
    user_repository.add(u2)
    db_session.commit()

    # Act
    target = user_repository.get_by_username("user_a")
    user_repository.delete(target)
    db_session.commit()

    # Assert: user_a sparisce, user_b rimane
    assert user_repository.get_by_username("user_a") is None
    assert user_repository.get_by_username("user_b") is not None
    assert len(user_repository.list_all()) == 1