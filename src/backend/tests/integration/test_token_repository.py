"""
Test di integrazione per TokenRepository.

Copertura al 100% dei metodi pubblici e dei campi del modello:
  - add()
  - get_by_token()   — trovato, non trovato
  - list_for_user()  — utente con token, utente senza token, isolamento cross-user

Campi del modello EmailVerificationToken verificati:
  - is_used    — default False, modificabile a True (caso d'uso reale: verifica email)
  - expires_at — persistito e recuperato correttamente
  - token (UNIQUE) — vincolo rispettato dal DB

La fixture token_repository è definita in conftest.py.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
import sqlalchemy.exc

from participium.models.token import EmailVerificationToken


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_token(user_id: int, token_str: str, **kwargs) -> EmailVerificationToken:
    """Crea un EmailVerificationToken con scadenza futura di default."""
    return EmailVerificationToken(
        user_id=user_id,
        token=token_str,
        expires_at=kwargs.pop("expires_at", datetime.now() + timedelta(hours=24)),
        **kwargs,
    )


def _truncate_to_second(dt: datetime) -> datetime:
    """Rimuove i microsecondi per confronti su DB che arrotondano al secondo (es. SQLite).

    """
    return dt.replace(microsecond=0)


# ---------------------------------------------------------------------------
# add()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_assigns_primary_key(token_repository, db_session):
    """add() persiste il token: dopo il commit l'id è valorizzato."""
    t = _make_token(user_id=1, token_str="token-pk-check")

    token_repository.add(t)
    db_session.commit()

    assert t.id is not None


@pytest.mark.integration
def test_add_returns_the_token_object(token_repository, db_session):
    """add() restituisce l'oggetto token passato (il type hint dice None, ma il codice fa return)."""
    t = _make_token(user_id=1, token_str="token-return-check")

    result = token_repository.add(t)
    db_session.commit()

    assert result is t


@pytest.mark.integration
def test_add_default_is_used_is_false(token_repository, db_session):
    """Il valore di default di is_used è False al momento della creazione."""
    t = _make_token(user_id=2, token_str="token-default-unused")

    token_repository.add(t)
    db_session.commit()
    db_session.expire(t)

    assert t.is_used is False


# ---------------------------------------------------------------------------
# get_by_token()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_get_by_token_returns_correct_token(token_repository, db_session):
    """get_by_token() recupera il token tramite la stringa token."""
    t = _make_token(user_id=1, token_str="secret-abc-123")

    token_repository.add(t)
    db_session.commit()

    fetched = token_repository.get_by_token("secret-abc-123")

    assert fetched is not None
    assert fetched.user_id == 1
    assert fetched.is_used is False


@pytest.mark.integration
def test_get_by_token_returns_none_when_not_found(token_repository):
    """get_by_token() restituisce None per una stringa token inesistente."""
    assert token_repository.get_by_token("does-not-exist") is None


# ---------------------------------------------------------------------------
# Campo is_used — comportamento reale del service
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_is_used_can_be_set_to_true(token_repository, db_session):
    """is_used può essere impostato a True per marcare il token come consumato.

    Questo è il caso d'uso reale: dopo la verifica email il token viene
    marcato usato per impedirne il riutilizzo.
    """
    t = _make_token(user_id=3, token_str="token-to-consume")
    token_repository.add(t)
    db_session.commit()

    fetched = token_repository.get_by_token("token-to-consume")
    fetched.is_used = True
    db_session.commit()

    updated = token_repository.get_by_token("token-to-consume")
    assert updated.is_used is True


# ---------------------------------------------------------------------------
# Campo expires_at
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_expires_at_is_persisted_correctly(token_repository, db_session):
    """expires_at viene persistito e recuperato con il valore corretto.

    Il confronto usa _truncate_to_second() perché SQLite arrotonda DateTime
    alla precisione del secondo.  Su PostgreSQL il confronto funziona anche
    senza troncamento; l'helper rende il test portabile tra i due backend.
    """
    expiry = datetime.now() + timedelta(hours=48)
    t = _make_token(user_id=4, token_str="token-expiry-check", expires_at=expiry)

    token_repository.add(t)
    db_session.commit()

    fetched = token_repository.get_by_token("token-expiry-check")
    assert _truncate_to_second(fetched.expires_at) == _truncate_to_second(expiry)


# ---------------------------------------------------------------------------
# Vincolo UNIQUE su token
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_duplicate_token_string_raises_integrity_error(token_repository, db_session):
    """Il vincolo UNIQUE su token.token viene rispettato: due token con la
    stessa stringa sollevano IntegrityError al momento del commit."""
    t1 = _make_token(user_id=1, token_str="duplicate-token")
    t2 = _make_token(user_id=2, token_str="duplicate-token")

    token_repository.add(t1)
    db_session.commit()

    token_repository.add(t2)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db_session.commit()


# ---------------------------------------------------------------------------
# list_for_user()
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_for_user_returns_only_that_users_tokens(token_repository, db_session):
    """list_for_user() filtra correttamente per user_id."""
    token_repository.add(_make_token(user_id=5, token_str="token-user5-A"))
    token_repository.add(_make_token(user_id=5, token_str="token-user5-B"))
    db_session.commit()

    results = token_repository.list_for_user(5)

    assert len(results) == 2
    assert {t.token for t in results} == {"token-user5-A", "token-user5-B"}


@pytest.mark.integration
def test_list_for_user_does_not_return_other_users_tokens(token_repository, db_session):
    """list_for_user() non restituisce token appartenenti ad altri utenti."""
    token_repository.add(_make_token(user_id=5, token_str="token-user5"))
    token_repository.add(_make_token(user_id=9, token_str="token-user9"))
    db_session.commit()

    results = token_repository.list_for_user(5)

    assert all(t.user_id == 5 for t in results)


@pytest.mark.integration
def test_list_for_user_returns_empty_list_for_unknown_user(token_repository):
    """list_for_user() restituisce lista vuota per un utente senza token."""
    assert token_repository.list_for_user(999) == []