from __future__ import annotations

import pytest

from participium.core.security import hash_password, verify_password


_CORRECT_PASSWORD = "secure123"
_CORRECT_HASH = hash_password(_CORRECT_PASSWORD)

# Casi di successo: password corretta 

@pytest.mark.parametrize(
    "password, password_hash, expected",
    [
        # PWD1 – password corretta
        (_CORRECT_PASSWORD, _CORRECT_HASH, True),
    ],
)
def test_verify_password_success(password, password_hash, expected) -> None:
    assert verify_password(password, password_hash) is expected



# Casi di fallimento: password non corrispondente 

@pytest.mark.parametrize(
    "password, password_hash",
    [
        # PWD2 – password errata
        ("wrong_pass", _CORRECT_HASH),
        # PWDB1 – password vuota
        ("", _CORRECT_HASH),
        # PWDB2 – hash vuoto
        (_CORRECT_PASSWORD, ""),
        # PWDB3 – entrambi vuoti
        ("", ""),
    ],
)
def test_verify_password_failure(password, password_hash) -> None:
    assert verify_password(password, password_hash) is False