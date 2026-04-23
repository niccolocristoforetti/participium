from __future__ import annotations

import pytest

from werkzeug.datastructures import FileStorage

from participium.core.exceptions import ValidationError
from participium.models.user import User
from participium.services.user_service import UserService


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

VALID_USER = User(
    id=201,
    username="mario.rossi",
    first_name="Mario",
    last_name="Rossi",
    is_active=True,
    is_email_verified=True,
    email_notifications_enabled=True,
)

# Utente il cui username sarà usato come duplicato
EXISTING_OTHER_USER = User(
    id=202,
    username="username.esistente",
    is_active=True,
    is_email_verified=True,
)

# Utente con notifiche email disabilitate (per test toggle)
USER_NOTIFICATIONS_OFF = User(
    id=203,
    username="giulia.neri",
    is_active=True,
    is_email_verified=True,
    email_notifications_enabled=False,
)


@pytest.fixture
def seed_update_profile_data() -> None:
    # Popola il sistema con i prerequisiti di `update_profile`.
    #
    # Dataset suggerito:
    # - `VALID_USER` persistito e attivo (id=201, username="mario.rossi")
    # - `EXISTING_OTHER_USER` persistito (id=202, username="username.esistente")
    # - `USER_NOTIFICATIONS_OFF` persistito (id=203, email_notifications_enabled=False)
    pass


# ---------------------------------------------------------------------------
# UP1 – Aggiornamento solo username
# EC covered: EC2 × EC5 × EC7 × EC9 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up1_update_username(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        username="nuovo.username",
    )

    assert isinstance(result, User)
    assert result.username == "nuovo.username"
    assert result.first_name == VALID_USER.first_name
    assert result.last_name == VALID_USER.last_name
    assert result.email_notifications_enabled == VALID_USER.email_notifications_enabled


# ---------------------------------------------------------------------------
# UP2 – Aggiornamento solo first_name
# EC covered: EC1 × EC6 × EC7 × EC9 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up2_update_first_name(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        first_name="NuovoNome",
    )

    assert isinstance(result, User)
    assert result.first_name == "NuovoNome"
    assert result.username == VALID_USER.username


# ---------------------------------------------------------------------------
# UP3 – Aggiornamento solo last_name
# EC covered: EC1 × EC5 × EC8 × EC9 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up3_update_last_name(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        last_name="NuovoCognome",
    )

    assert isinstance(result, User)
    assert result.last_name == "NuovoCognome"
    assert result.username == VALID_USER.username


# ---------------------------------------------------------------------------
# UP4 – Disabilitare notifiche email (True → False)
# EC covered: EC1 × EC5 × EC7 × EC10 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up4_disable_email_notifications(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        email_notifications_enabled=False,
    )

    assert isinstance(result, User)
    assert result.email_notifications_enabled is False


# ---------------------------------------------------------------------------
# UP5 – Abilitare notifiche email (False → True)
# EC covered: EC1 × EC5 × EC7 × EC11 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up5_enable_email_notifications(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=USER_NOTIFICATIONS_OFF,
        email_notifications_enabled=True,
    )

    assert isinstance(result, User)
    assert result.email_notifications_enabled is True


# ---------------------------------------------------------------------------
# UP6 – Aggiornamento immagine profilo
# EC covered: EC1 × EC5 × EC7 × EC9 × EC13
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up6_update_profile_picture(seed_update_profile_data: None) -> None:
    service = UserService()
    photo = FileStorage(filename="avatar.png", content_type="image/png")

    result = service.update_profile(
        user=VALID_USER,
        profile_picture=photo,
    )

    assert isinstance(result, User)
    assert result.profile_picture_path is not None


# ---------------------------------------------------------------------------
# UP7 – Aggiornamento di tutti i campi
# EC covered: EC2 × EC6 × EC8 × EC11 × EC13
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up7_update_all_fields(seed_update_profile_data: None) -> None:
    service = UserService()
    photo = FileStorage(filename="pic.jpg", content_type="image/jpeg")

    result = service.update_profile(
        user=VALID_USER,
        username="altro.username",
        first_name="Mario",
        last_name="Verdi",
        email_notifications_enabled=True,
        profile_picture=photo,
    )

    assert isinstance(result, User)
    assert result.username == "altro.username"
    assert result.first_name == "Mario"
    assert result.last_name == "Verdi"
    assert result.email_notifications_enabled is True
    assert result.profile_picture_path is not None


# ---------------------------------------------------------------------------
# UP8 – Nessun campo aggiornato (tutti None)
# EC covered: EC1 × EC5 × EC7 × EC9 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up8_no_changes(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(user=VALID_USER)

    assert isinstance(result, User)
    assert result.username == VALID_USER.username
    assert result.first_name == VALID_USER.first_name
    assert result.last_name == VALID_USER.last_name
    assert result.email_notifications_enabled == VALID_USER.email_notifications_enabled


# ---------------------------------------------------------------------------
# UP9 – Username uguale al proprio corrente → nessun conflitto
# EC covered: EC4 × EC5 × EC7 × EC9 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up9_same_username(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        username="mario.rossi",
    )

    assert isinstance(result, User)
    assert result.username == "mario.rossi"


# ---------------------------------------------------------------------------
# UP10 – Username già in uso da un altro account → ValidationError
# EC covered: EC3 × EC5 × EC7 × EC9 × EC12
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="Disabled.")
def test_up10_duplicate_username(seed_update_profile_data: None) -> None:
    service = UserService()

    with pytest.raises(ValidationError):
        service.update_profile(
            user=VALID_USER,
            username="username.esistente",
        )


# ---------------------------------------------------------------------------
# Boundary: campi vuoti
# Il contratto non documenta eccezioni per stringhe vuote.
# ---------------------------------------------------------------------------

# UPB1 – Username stringa vuota
# Il contratto documenta ValidationError solo per username già in uso da
# un altro account, non per username vuoto. L'implementazione potrebbe
# ragionevolmente rifiutare anche questo caso; da verificare alla consegna.
# EC covered: EC2 × EC5 × EC7 × EC9 × EC12
@pytest.mark.skip(reason="Disabled.")
def test_upb1_empty_username(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        username="",
    )

    assert isinstance(result, User)
    assert result.username == ""


# UPB2 – first_name stringa vuota
# EC covered: EC1 × EC6 × EC7 × EC9 × EC12
@pytest.mark.skip(reason="Disabled.")
def test_upb2_empty_first_name(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        first_name="",
    )

    assert isinstance(result, User)
    assert result.first_name == ""


# UPB3 – last_name stringa vuota
# EC covered: EC1 × EC5 × EC8 × EC9 × EC12
@pytest.mark.skip(reason="Disabled.")
def test_upb3_empty_last_name(seed_update_profile_data: None) -> None:
    service = UserService()

    result = service.update_profile(
        user=VALID_USER,
        last_name="",
    )

    assert isinstance(result, User)
    assert result.last_name == ""


# ---------------------------------------------------------------------------
# Boundary: immagine profilo
# Il contratto di update_profile non documenta eccezioni per profile_picture
# con filename assente o vuoto; in create_report un vincolo analogo è invece
# documentato. Da verificare alla consegna del codice.
# ---------------------------------------------------------------------------

# UPB4 – FileStorage senza filename
# EC covered: EC1 × EC5 × EC7 × EC9 × EC13
@pytest.mark.skip(reason="Disabled.")
def test_upb4_picture_no_filename(seed_update_profile_data: None) -> None:
    service = UserService()
    photo = FileStorage(filename=None)

    result = service.update_profile(
        user=VALID_USER,
        profile_picture=photo,
    )

    assert isinstance(result, User)


# UPB5 – FileStorage con filename vuoto
# EC covered: EC1 × EC5 × EC7 × EC9 × EC13
@pytest.mark.skip(reason="Disabled.")
def test_upb5_picture_empty_filename(seed_update_profile_data: None) -> None:
    service = UserService()
    photo = FileStorage(filename="")

    result = service.update_profile(
        user=VALID_USER,
        profile_picture=photo,
    )

    assert isinstance(result, User)
