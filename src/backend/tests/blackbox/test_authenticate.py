from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Disabled.")

from participium.core.exceptions import AuthenticationError
from participium.models.user import User
from participium.services.auth_service import AuthService


CORRECT_PASSWORD = "correct_password"
WRONG_PASSWORD = "wrong_password"


@pytest.fixture
def seed_authenticate_data() -> None:
    # Popola il sistema con i prerequisiti di `authenticate`.
    #
    # Dataset suggerito:
    # - Utente attivo, email verificata, username "mario.rossi", email "mario.rossi@example.com"
    # - Utente inattivo, username "inactive.user", email "inactive.user@example.com"
    # - Utente attivo, email non verificata, username "unverified.user", email "unverified.user@example.com"
    pass


def test_auth1_valid_username(seed_authenticate_data: None) -> None:
    user = AuthService().authenticate("mario.rossi", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.username == "mario.rossi"


def test_auth2_valid_email(seed_authenticate_data: None) -> None:
    user = AuthService().authenticate("mario.rossi@example.com", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.email == "mario.rossi@example.com"


def test_auth3_unknown_username(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("unknown_user", "any_password")


def test_auth4_unknown_email(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("unknown_user@example.com", "any_password")


def test_auth5_wrong_password_username(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("mario.rossi", WRONG_PASSWORD)


def test_auth6_wrong_password_email(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("mario.rossi@example.com", WRONG_PASSWORD)


def test_auth7_inactive_user_username(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("inactive.user", CORRECT_PASSWORD)


def test_auth8_inactive_user_email(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("inactive.user@example.com", CORRECT_PASSWORD)


def test_auth9_unverified_email_by_email(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("unverified.user@example.com", CORRECT_PASSWORD)


def test_auth10_unverified_email_by_username(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("unverified.user", CORRECT_PASSWORD)


def test_auth11_empty_identifier(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("", "any_password")


def test_auth12_empty_password_username(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("mario.rossi", "")


def test_auth13_empty_password_email(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("mario.rossi@example.com", "")


def test_auth14_both_empty(seed_authenticate_data: None) -> None:
    with pytest.raises(AuthenticationError):
        AuthService().authenticate("", "")


def test_auth15_email_with_leading_trailing_spaces(seed_authenticate_data: None) -> None:
    user = AuthService().authenticate(" mario.rossi@example.com ", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.email == "mario.rossi@example.com"


def test_auth16_email_with_uppercase_chars(seed_authenticate_data: None) -> None:
    user = AuthService().authenticate("Mario.Rossi@Example.Com", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.email == "mario.rossi@example.com"


def test_auth17_username_with_leading_trailing_spaces(seed_authenticate_data: None) -> None:
    user = AuthService().authenticate(" mario.rossi ", CORRECT_PASSWORD)
    assert isinstance(user, User)
    assert user.username == "mario.rossi"
