from __future__ import annotations

import pytest

from participium.core.security import verify_password


# ---------------------------------------------------------------------------
# PWD1 – Password corretta → True
# EC covered: EC1
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_pwd1_correct_password() -> None:
    result = verify_password("secure123", "hash_di_secure123")

    assert result is True


# ---------------------------------------------------------------------------
# PWD2 – Password errata → False
# EC covered: EC2
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_pwd2_wrong_password() -> None:
    result = verify_password("wrong_pass", "hash_di_secure123")

    assert result is False


# ---------------------------------------------------------------------------
# Boundary: input strutturalmente vuoti
# Il contratto non specifica il comportamento su stringhe vuote;
# i test seguenti verificano l'ipotesi che nessuna password corrisponda
# a un hash vuoto e viceversa.
# ---------------------------------------------------------------------------

# PWDB1 – Password vuota → False
# EC covered: EC2
@pytest.mark.skip(reason="Disabled.")
def test_pwdb1_empty_password() -> None:
    result = verify_password("", "hash_di_secure123")

    assert result is False


# PWDB2 – Hash vuoto → False
# EC covered: EC2
@pytest.mark.skip(reason="Disabled.")
def test_pwdb2_empty_hash() -> None:
    result = verify_password("secure123", "")

    assert result is False


# PWDB3 – Entrambi vuoti → False
# EC covered: EC2
@pytest.mark.skip(reason="Disabled.")
def test_pwdb3_both_empty() -> None:
    result = verify_password("", "")

    assert result is False