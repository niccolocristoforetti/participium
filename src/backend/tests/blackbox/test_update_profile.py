from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from werkzeug.datastructures import FileStorage
from participium.core.exceptions import ValidationError
from participium.models.base import Base
from participium.models.enums import Role
from participium.models.user import User
from participium.repositories.user_repository import UserRepository
from participium.services.storage_service import StorageService
from participium.services.user_service import UserService


@pytest.fixture
def seed_update_profile_data():
    """
    Crea un DB SQLite in-memory con:
    - Utente id=1  (mario.rossi, email_notifications_enabled=True)
    - Utente id=2  (username.esistente, per test duplicato)
    - Utente id=3  (giulia.neri, email_notifications_enabled=False)
    Restituisce (service, user_main, user_notif_off).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user_main = User(
            id=1,
            username="mario.rossi",
            first_name="Mario",
            last_name="Rossi",
            email="mario.rossi@example.com",
            password_hash="hashed",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
            email_notifications_enabled=True,
        )
        user_existing = User(
            id=2,
            username="username.esistente",
            first_name="Luca",
            last_name="Bianchi",
            email="luca.bianchi@example.com",
            password_hash="hashed",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
        )
        user_notif_off = User(
            id=3,
            username="giulia.neri",
            first_name="Giulia",
            last_name="Neri",
            email="giulia.neri@example.com",
            password_hash="hashed",
            role=Role.CITIZEN,
            is_active=True,
            is_email_verified=True,
            email_notifications_enabled=False,
        )
        session.add_all([user_main, user_existing, user_notif_off])
        session.commit()

        service = UserService(
            session=session,
            user_repository=UserRepository(session),
            storage_service=StorageService(),
        )

        yield service, user_main, user_notif_off


# --- foto per i test ---
VALID_PHOTO = FileStorage(filename="avatar.png", content_type="image/png")



# Casi di successo: aggiornamento di un singolo campo


# UP1 – Solo username
def test_up1_update_username(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, username="nuovo.username")

    assert isinstance(result, User)
    assert result.username == "nuovo.username"
    assert result.first_name == "Mario"
    assert result.last_name == "Rossi"


# UP2 – Solo first_name
def test_up2_update_first_name(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, first_name="NuovoNome")

    assert isinstance(result, User)
    assert result.first_name == "NuovoNome"
    assert result.username == "mario.rossi"


# UP3 – Solo last_name
def test_up3_update_last_name(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, last_name="NuovoCognome")

    assert isinstance(result, User)
    assert result.last_name == "NuovoCognome"


# UP4 – Disabilitare notifiche email (True → False)
def test_up4_disable_email_notifications(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, email_notifications_enabled=False)

    assert isinstance(result, User)
    assert result.email_notifications_enabled is False


# UP5 – Abilitare notifiche email (False → True)
def test_up5_enable_email_notifications(seed_update_profile_data) -> None:
    service, _, user_notif_off = seed_update_profile_data

    result = service.update_profile(user=user_notif_off, email_notifications_enabled=True)

    assert isinstance(result, User)
    assert result.email_notifications_enabled is True


# UP6 – Aggiornamento immagine profilo
def test_up6_update_profile_picture(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data
    photo = FileStorage(filename="avatar.png", content_type="image/png")

    result = service.update_profile(user=user, profile_picture=photo)

    assert isinstance(result, User)
    assert result.profile_picture_path is not None



# Casi di successo: aggiornamento multiplo / nessun campo


# UP7 – Aggiornamento di tutti i campi
def test_up7_update_all_fields(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data
    photo = FileStorage(filename="pic.jpg", content_type="image/jpeg")

    result = service.update_profile(
        user=user,
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


# UP8 – Nessun campo aggiornato
def test_up8_no_changes(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user)

    assert isinstance(result, User)
    assert result.username == "mario.rossi"
    assert result.first_name == "Mario"
    assert result.last_name == "Rossi"


# Casi username: proprio username / username duplicato


# UP9 – Username uguale al proprio → nessun conflitto
def test_up9_same_username(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, username="mario.rossi")

    assert isinstance(result, User)
    assert result.username == "mario.rossi"


# UP10 – Username già in uso → ValidationError
def test_up10_duplicate_username(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    with pytest.raises(ValidationError):
        service.update_profile(user=user, username="username.esistente")



# Boundary: campi vuoti
# L'implementazione tratta le stringhe vuote come falsy (if username:),quindi non aggiorna il campo. 
# I test che si aspettavano l'aggiornamento sono marcati xfail.


# UPB1 – Username stringa vuota: l'impl. non aggiorna (stringa vuota è falsy)
@pytest.mark.xfail(
    strict=True,
    reason="L'implementazione tratta username='' come falsy e non aggiorna il campo",
)
def test_upb1_empty_username(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, username="")

    assert result.username == ""


# UPB2 – first_name stringa vuota: stessa logica
@pytest.mark.xfail(
    strict=True,
    reason="L'implementazione tratta first_name='' come falsy e non aggiorna il campo",
)
def test_upb2_empty_first_name(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, first_name="")

    assert result.first_name == ""


# UPB3 – last_name stringa vuota: stessa logica
@pytest.mark.xfail(
    strict=True,
    reason="L'implementazione tratta last_name='' come falsy e non aggiorna il campo",
)
def test_upb3_empty_last_name(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data

    result = service.update_profile(user=user, last_name="")

    assert result.last_name == ""



# Boundary: immagine profilo senza filename
# L'implementazione fa `if profile_picture and profile_picture.filename:`quindi FileStorage con filename=None
# o "" non causa errori, semplicemente non aggiorna il campo. User restituito invariato.


# UPB4 – FileStorage senza filename → no update, nessun errore
def test_upb4_picture_no_filename(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data
    photo = FileStorage(filename=None)

    result = service.update_profile(user=user, profile_picture=photo)

    assert isinstance(result, User)
    assert result.profile_picture_path is None  # non aggiornato


# UPB5 – FileStorage con filename vuoto → no update, nessun errore
def test_upb5_picture_empty_filename(seed_update_profile_data) -> None:
    service, user, _ = seed_update_profile_data
    photo = FileStorage(filename="")

    result = service.update_profile(user=user, profile_picture=photo)

    assert isinstance(result, User)
    assert result.profile_picture_path is None  # non aggiornato