from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from participium.core.exceptions import ValidationError
from participium.models.enums import Role
from participium.models.user import User
from participium.services.user_service import UserService


pytestmark = pytest.mark.whitebox


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user(
    *,
    user_id: int = 1,
    username: str = "mario.rossi",
    email: str = "mario@ex.com",
    first_name: str = "Mario",
    last_name: str = "Rossi",
    role: Role = Role.CITIZEN,
    category_id: int | None = None,
    is_active: bool = True,
    email_notifications_enabled: bool = True,
) -> User:
    return User(
        id=user_id,
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        role=role,
        category_id=category_id,
        is_active=is_active,
        email_notifications_enabled=email_notifications_enabled,
    )


# ---------------------------------------------------------------------------
# Fixture: service con tutte le dipendenze mockate
# ---------------------------------------------------------------------------

@pytest.fixture
def service_bundle() -> dict[str, object]:
    session = Mock()
    user_repository = Mock()
    category_repository = Mock()
    service = UserService(
        session=session,
        user_repository=user_repository,
        category_repository=category_repository,
    )
    # get_user restituisce un utente di default
    service.get_user = Mock(return_value=_user())
    return {
        "service": service,
        "session": session,
        "user_repository": user_repository,
    }


# ---------------------------------------------------------------------------
# T1 — Username duplicato → raise ValidationError
# Nodi: N1→N2→N3 | Condition: C1a=T, C1b=T, C1c=T | Path P1
# ---------------------------------------------------------------------------
def test_t1_username_already_in_use(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]
    user_repo.get_by_username.return_value = _user(user_id=99, username="taken")

    with pytest.raises(ValidationError, match="Username already in use"):
        service.update_user(user_id=1, payload={"username": "taken"})

    user_repo.get_by_username.assert_called_once_with("taken")


# ---------------------------------------------------------------------------
# T2 — Email duplicata → raise ValidationError
# Nodi: N1→N2→N4→N5 | Condition: C2a=T, C2b=T, C2c=T | Path P2
# ---------------------------------------------------------------------------
def test_t2_email_already_in_use(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = _user(user_id=99, email="taken@ex.com")

    with pytest.raises(ValidationError, match="Email already in use"):
        service.update_user(user_id=1, payload={"email": "taken@ex.com"})

    user_repo.get_by_email.assert_called_once_with("taken@ex.com")


# ---------------------------------------------------------------------------
# T3 — Payload vuoto → nessuna modifica, tutti i rami False
# Edge: tutti i rami False | Condition: C1a=F, C2a=F, C3=F×4, C4=F,
#   C5a=F, C5b=F, C7=F, C8=F | Path P3 | Loop: C3=F×4
# ---------------------------------------------------------------------------
def test_t3_empty_payload(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    session: Mock = service_bundle["session"]

    result = service.update_user(user_id=1, payload={})

    assert isinstance(result, User)
    assert result.username == "mario.rossi"
    assert result.email == "mario@ex.com"
    assert result.role == Role.CITIZEN
    assert result.is_active is True
    assert result.email_notifications_enabled is True
    session.commit.assert_called_once()


# ---------------------------------------------------------------------------
# T4 — Payload completo → tutti i rami True, tutte le modifiche applicate
# Node: tutti | Edge: tutti i rami True | Condition: C1c=F, C2c=F,
#   C3=T×4, C4=T, C5a=T, C6=T, C7=T, C8=T | Path P4 | Loop: C3=T×4
# ---------------------------------------------------------------------------
def test_t4_full_payload_all_fields(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    session: Mock = service_bundle["session"]
    user_repo: Mock = service_bundle["user_repository"]
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = None

    mock_category = Mock(id=5)
    service._parse_role = Mock(return_value=Role.OPERATOR)
    service._resolve_operator_category = Mock(return_value=mock_category)

    payload = {
        "username": " new_user ",
        "first_name": " Mario ",
        "last_name": " Verdi ",
        "email": " new@ex.com ",
        "role": "operator",
        "category_id": 5,
        "is_active": True,
        "email_notifications_enabled": False,
    }

    result = service.update_user(user_id=1, payload=payload)

    assert isinstance(result, User)
    assert result.username == "new_user"
    assert result.first_name == "Mario"
    assert result.last_name == "Verdi"
    assert result.email == "new@ex.com"
    assert result.role == Role.OPERATOR
    assert result.category_id == 5
    assert result.is_active is True
    assert result.email_notifications_enabled is False
    session.commit.assert_called_once()
    service._parse_role.assert_called_once_with("operator")
    service._resolve_operator_category.assert_called_once()


# ---------------------------------------------------------------------------
# T5 — Username uguale all'attuale → C1a=T, C1b=F (short-circuit)
# Path P5 | Loop: C3 mix (1 True, 3 False)
# ---------------------------------------------------------------------------
def test_t5_username_same_as_current(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]

    result = service.update_user(user_id=1, payload={"username": "mario.rossi"})

    assert isinstance(result, User)
    assert result.username == "mario.rossi"
    user_repo.get_by_username.assert_not_called()


# ---------------------------------------------------------------------------
# T6 — Email uguale all'attuale → C2a=T, C2b=F (short-circuit)
# Path P6
# ---------------------------------------------------------------------------
def test_t6_email_same_as_current(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]

    result = service.update_user(user_id=1, payload={"email": "mario@ex.com"})

    assert isinstance(result, User)
    assert result.email == "mario@ex.com"
    user_repo.get_by_email.assert_not_called()


# ---------------------------------------------------------------------------
# T7 — Solo category_id, no role → C5a=T (short-circuit or), C4=F, C6=F
#   _resolve_operator_category chiamata con user.role; restituisce None
#   → user.category_id diventa None (N13a→N13c) | Path P7
# ---------------------------------------------------------------------------
def test_t7_category_id_only_no_role(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    service._resolve_operator_category = Mock(return_value=None)

    result = service.update_user(user_id=1, payload={"category_id": 3})

    assert isinstance(result, User)
    assert result.category_id is None
    service._resolve_operator_category.assert_called_once_with(
        Role.CITIZEN, 3
    )


# ---------------------------------------------------------------------------
# T8 — Solo role, no category_id → C5a=F, C5b=T; C4=T, C6=T
#   _parse_role + _resolve_operator_category chiamati (N13a→N13b) | Path P8
# ---------------------------------------------------------------------------
def test_t8_role_only_no_category_id(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    mock_category = Mock(id=10)
    service._parse_role = Mock(return_value=Role.ADMIN)
    service._resolve_operator_category = Mock(return_value=mock_category)

    result = service.update_user(user_id=1, payload={"role": "admin"})

    assert isinstance(result, User)
    assert result.role == Role.ADMIN
    assert result.category_id == 10
    service._parse_role.assert_called_once_with("admin")
    service._resolve_operator_category.assert_called_once()
