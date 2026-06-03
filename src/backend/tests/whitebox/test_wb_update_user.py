from __future__ import annotations

from unittest.mock import Mock, patch
import pytest

from participium.core.exceptions import ValidationError
from participium.models.enums import Role
from participium.models.user import User
from participium.services.user_service import UserService


pytestmark = pytest.mark.whitebox



#  Helpers 


#  crea un'istanza reale del modello User compilata con dati di default.
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



#  Fixtures 


# Prepara l'ambiente isolando UserService e configurando il recupero di un utente di default.
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
    service.get_user = Mock(return_value=_user())
    return {
        "service": service,
        "session": session,
        "user_repository": user_repository,
    }



#  Casi di Test 


# UU1 – verifica il sollevamento di una ValidationError se lo username richiesto nel payload è già associato a un altro utente.
def test_uu1_username_already_in_use(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]
    user_repo.get_by_username.return_value = _user(user_id=99, username="taken")

    with pytest.raises(ValidationError, match="Username already in use"):
        service.update_user(user_id=1, payload={"username": "taken"})

    user_repo.get_by_username.assert_called_once_with("taken")


# UU2 – verifica il sollevamento di una ValidationError se l'indirizzo email richiesto nel payload è già associato a un altro utente.
def test_uu2_email_already_in_use(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]
    user_repo.get_by_username.return_value = None
    user_repo.get_by_email.return_value = _user(user_id=99, email="taken@ex.com")

    with pytest.raises(ValidationError, match="Email already in use"):
        service.update_user(user_id=1, payload={"email": "taken@ex.com"})

    user_repo.get_by_email.assert_called_once_with("taken@ex.com")


# UUB1 – verifica che l'invio di un payload privo di campi non modifichi l'utente corrente e salvi le modifiche correnti.
def test_uub1_empty_payload(service_bundle: dict[str, object]) -> None:
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


# UU3 – verifica la corretta applicazione, sanificazione (strip) e persistenza di tutti i campi modificabili presenti nel dizionario.
def test_uu3_full_payload_all_fields(service_bundle: dict[str, object]) -> None:
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


# UU4 – verifica che se lo username inviato coincide con quello attuale, il controllo di unicità sul database venga saltato.
def test_uu4_username_same_as_current(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]

    result = service.update_user(user_id=1, payload={"username": "mario.rossi"})

    assert isinstance(result, User)
    assert result.username == "mario.rossi"
    user_repo.get_by_username.assert_not_called()


# UU5 – verifica che se l'email inviata coincide con quella attuale, il controllo di unicità sul database venga saltato.
def test_uu5_email_same_as_current(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    user_repo: Mock = service_bundle["user_repository"]

    result = service.update_user(user_id=1, payload={"email": "mario@ex.com"})

    assert isinstance(result, User)
    assert result.email == "mario@ex.com"
    user_repo.get_by_email.assert_not_called()


# UU6 – verifica che l'invio del solo category_id aggiorni la categoria dell'operatore interpellando il risolutore interno del servizio.
def test_uu6_category_id_only_no_role(service_bundle: dict[str, object]) -> None:
    service: UserService = service_bundle["service"]
    service._resolve_operator_category = Mock(return_value=None)

    result = service.update_user(user_id=1, payload={"category_id": 3})

    assert isinstance(result, User)
    assert result.category_id is None
    service._resolve_operator_category.assert_called_once_with(Role.CITIZEN, 3)


# UU7 – verifica che l'invio del solo ruolo aggiorni i permessi dell'utente e ricalcoli la categoria di competenza associata.
def test_uu7_role_only_no_category_id(service_bundle: dict[str, object]) -> None:
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