"""
Test di integrazione per UserRepository.

Copertura al 100% dei metodi pubblici:
  - add()
  - get_by_id()                — trovato, non trovato
  - get_by_email()             — trovato, non trovato
  - get_by_username()          — trovato, non trovato
  - get_by_username_or_email() — trovato per username, per email, non trovato
  - list_all()                 — ordinamento DESC per created_at, lista vuota
  - delete()                   — rimozione, isolamento da altri utenti

La fixture user_repository è definita in conftest.py.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from participium.models.user import User
from participium.models.notification import Notification
from participium.models.enums import NotificationType, Role
from participium.models.token import EmailVerificationToken


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_user(username: str, email: str, **kwargs) -> User:
    """Costruisce un User con i campi obbligatori e valori di default sensati."""
    return User(
        username=username,
        first_name=kwargs.pop("first_name", "Nome"),
        last_name=kwargs.pop("last_name", "Cognome"),
        email=email,
        password_hash=kwargs.pop("password_hash", "fakehash"),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_assigns_primary_key(user_repository, db_session):
    """add() persiste l'utente: dopo il commit l'id è valorizzato."""
    user = _make_user(username="user.pk", email="pk@test.com")

    user_repository.add(user)
    db_session.commit()

    assert user.id is not None


@pytest.mark.integration
def test_add_returns_the_same_object(user_repository, db_session):
    """add() restituisce l'oggetto passato (identità, non copia)."""
    user = _make_user(username="user.ret", email="ret@test.com")

    result = user_repository.add(user)
    db_session.commit()

    assert result is user


@pytest.mark.integration
def test_add_default_values(user_repository, db_session):
    """I valori di default per un nuovo utente sono:
      - role = Role.CITIZEN
      - is_active = True
      - is_email_verified = False
      - email_notifications_enabled = True
    """
    user = _make_user(username="user.defaults", email="defaults@test.com")

    user_repository.add(user)
    db_session.commit()
    db_session.expire(user)

    assert user.role == Role.CITIZEN
    assert user.is_active is True
    assert user.is_email_verified is False
    assert user.email_notifications_enabled is True


# ---------------------------------------------------------------------------
# get_by_id()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_id_returns_correct_user(user_repository, db_session):
    """get_by_id() recupera l'utente con l'id corretto."""
    user = _make_user(username="mario.rossi", email="mario@example.com",
                      first_name="Mario", last_name="Rossi")

    user_repository.add(user)
    db_session.commit()

    fetched = user_repository.get_by_id(user.id)

    assert fetched is not None
    assert fetched.username == "mario.rossi"
    assert fetched.first_name == "Mario"


@pytest.mark.integration
def test_get_by_id_returns_none_for_missing_user(user_repository):
    """get_by_id() restituisce None per un id inesistente."""
    assert user_repository.get_by_id(999) is None


# ---------------------------------------------------------------------------
# get_by_email()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_email_returns_correct_user(user_repository, db_session):
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
# get_by_username()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_username_returns_correct_user(user_repository, db_session):
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
# get_by_username_or_email()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_username_or_email_found_by_username(user_repository, db_session):
    """get_by_username_or_email() trova l'utente cercando per username."""
    user = _make_user(username="utente1", email="utente1@example.com")

    user_repository.add(user)
    db_session.commit()

    result = user_repository.get_by_username_or_email("utente1")

    assert result is not None
    assert result.email == "utente1@example.com"


@pytest.mark.integration
def test_get_by_username_or_email_found_by_email(user_repository, db_session):
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
# list_all()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_all_returns_empty_list_when_no_users(user_repository):
    """list_all() restituisce una lista vuota quando non ci sono utenti."""
    assert user_repository.list_all() == []


@pytest.mark.integration
def test_list_all_orders_by_created_at_desc(user_repository, db_session):
    """list_all() include tutti gli utenti e li ordina dal più recente al più vecchio.

    I created_at vengono impostati sull'istanza dopo la costruzione per evitare
    di passare argomenti non dichiarati nel costruttore di User.
    I dati vengono inseriti in ordine inverso rispetto a quello atteso, così
    l'ordinamento è verificato dalla query e non dall'ordine di inserimento.
    """
    now = datetime.now()
    u_old = _make_user(username="user_old", email="old@test.com")
    u_new = _make_user(username="user_new", email="new@test.com")

    u_old.created_at = now - timedelta(seconds=2)
    u_new.created_at = now

    # Inserimento in ordine inverso rispetto all'atteso
    user_repository.add(u_old)
    user_repository.add(u_new)
    db_session.commit()

    results = user_repository.list_all()

    assert len(results) == 2
    assert results[0].username == "user_new"
    assert results[1].username == "user_old"


# ---------------------------------------------------------------------------
# delete()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_delete_removes_user_and_does_not_affect_others(user_repository, db_session):
    """delete() rimuove l'utente target mantenendo intatti gli altri.

    Un unico test che verifica sia la rimozione dell'utente eliminato sia
    l'integrità degli altri, evitando la duplicazione del setup.
    """
    u1 = _make_user(username="user_a", email="a@test.com")
    u2 = _make_user(username="user_b", email="b@test.com")

    user_repository.add(u1)
    user_repository.add(u2)
    db_session.commit()

    user_repository.delete(u1)
    db_session.commit()

    assert user_repository.get_by_username("user_a") is None
    assert user_repository.get_by_username("user_b") is not None
    assert len(user_repository.list_all()) == 1


# ---------------------------------------------------------------------------
# Comportamento del Modello: Cascade Delete
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_delete_user_cascades_to_notifications_and_tokens(
    user_repository, notification_repository, token_repository, db_session
):
    """Eliminando un utente vengono rimossi in cascata sia le notifiche che i token.

    Le due cascade vengono verificate su un singolo utente eliminato per evitare
    la duplicazione del setup presente nella versione con test separati.
    """
    user = _make_user(username="cascade_user", email="cascade@test.com")
    user_repository.add(user)
    db_session.commit()

    db_session.add(Notification(
        user_id=user.id, type=NotificationType.SYSTEM, title="Sys", body="Body",
    ))
    db_session.add(EmailVerificationToken(
        user_id=user.id, token="tok-cascade", expires_at=datetime.now() + timedelta(days=1),
    ))
    db_session.commit()

    user_repository.delete(user)
    deleted_user_id = user.id
    db_session.commit()

    assert notification_repository.list_for_user(deleted_user_id)== []
    assert token_repository.list_for_user(deleted_user_id) == []