from __future__ import annotations

from participium.core.security import hash_password, verify_password


_CORRECT_PASSWORD = "secure123"
_CORRECT_HASH = hash_password(_CORRECT_PASSWORD)


# PWD1 – Password corretta → True
def test_pwd1_correct_password() -> None:
    assert verify_password(_CORRECT_PASSWORD, _CORRECT_HASH) is True


# PWD2 – Password errata → False
def test_pwd2_wrong_password() -> None:
    assert verify_password("wrong_pass", _CORRECT_HASH) is False


# PWDB1 – Password vuota → False
def test_pwdb1_empty_password() -> None:
    assert verify_password("", _CORRECT_HASH) is False


# PWDB2 – Hash vuoto → False
def test_pwdb2_empty_hash() -> None:
    assert verify_password(_CORRECT_PASSWORD, "") is False


# PWDB3 – Entrambi vuoti → False
def test_pwdb3_both_empty() -> None:
    assert verify_password("", "") is False