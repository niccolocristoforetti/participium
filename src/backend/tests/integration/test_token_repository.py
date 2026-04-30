"""
Test di integrazione per TokenRepository.

Copertura al 100% dei metodi pubblici e dei campi del modello:
  - add()
  - get_by_token()   — trovato, non trovato
  - list_for_user()  — utente con token, utente senza token

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


# ---------------------------------------------------------------------------
# ADD / GET_BY_TOKEN
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_add_and_get_by_token_found(token_repository, db_session):
    """add() persiste il token; get_by_token() lo recupera per stringa."""
    # Arrange
    new_token = _make_token(user_id=1, token_str="secret-abc-123")

    # Act
    token_repository.add(new_token)
    db_session.commit()

    # Assert
    fetched = token_repository.get_by_token("secret-abc-123")
    assert fetched is not None
    assert fetched.user_id == 1
    assert fetched.is_used is False  # valore di default


@pytest.mark.integration
def test_get_by_token_returns_none_when_not_found(token_repository):
    """get_by_token() restituisce None per una stringa token inesistente."""
    assert token_repository.get_by_token("does-not-exist") is None


# ---------------------------------------------------------------------------
# CAMPO is_used
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_is_used_default_is_false(token_repository, db_session):
    """Il valore di default di is_used è False al momento della creazione."""
    token = _make_token(user_id=2, token_str="token-default-unused")
    token_repository.add(token)
    db_session.commit()

    fetched = token_repository.get_by_token("token-default-unused")
    assert fetched.is_used is False


@pytest.mark.integration
def test_is_used_can_be_set_to_true(token_repository, db_session):
    """is_used può essere impostato a True per marcare il token come consumato.

    Questo è il caso d'uso reale: dopo la verifica email il token viene
    marcato usato per impedirne il riutilizzo.
    """
    # Arrange
    token = _make_token(user_id=3, token_str="token-to-consume")
    token_repository.add(token)
    db_session.commit()

    # Act — simula la logica del service che consuma il token
    fetched = token_repository.get_by_token("token-to-consume")
    fetched.is_used = True
    db_session.commit()

    # Assert — la modifica è stata persistita
    updated = token_repository.get_by_token("token-to-consume")
    assert updated.is_used is True


# ---------------------------------------------------------------------------
# CAMPO expires_at
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_expires_at_is_persisted_correctly(token_repository, db_session):
    """expires_at viene persistito e recuperato con il valore corretto.

    Il confronto tollera meno di 1 secondo di scarto perché SQLite può
    arrotondare i microsecondi in modo diverso da Python.
    """
    expiry = datetime.now() + timedelta(hours=48)
    token = _make_token(user_id=4, token_str="token-expiry-check", expires_at=expiry)
    token_repository.add(token)
    db_session.commit()

    fetched = token_repository.get_by_token("token-expiry-check")
    assert abs((fetched.expires_at - expiry).total_seconds()) < 1


# ---------------------------------------------------------------------------
# VINCOLO UNIQUE su token
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
# LIST_FOR_USER
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_list_for_user_returns_only_that_users_tokens(token_repository, db_session):
    """list_for_user() filtra correttamente per user_id."""
    t1 = _make_token(user_id=5, token_str="token-user5-A")
    t2 = _make_token(user_id=5, token_str="token-user5-B")
    t3 = _make_token(user_id=9, token_str="token-user9-A")

    token_repository.add(t1)
    token_repository.add(t2)
    token_repository.add(t3)
    db_session.commit()

    user5_tokens = token_repository.list_for_user(5)
    user9_tokens = token_repository.list_for_user(9)

    assert len(user5_tokens) == 2
    assert {t.token for t in user5_tokens} == {"token-user5-A", "token-user5-B"}

    assert len(user9_tokens) == 1
    assert user9_tokens[0].token == "token-user9-A"


@pytest.mark.integration
def test_list_for_user_returns_empty_list_for_unknown_user(token_repository):
    """list_for_user() restituisce lista vuota per un utente senza token."""
    assert token_repository.list_for_user(999) == []