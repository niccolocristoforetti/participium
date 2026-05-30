"""
Test di accettazione Selenium per la dashboard del cittadino (/dashboard):

  UC-15 – Gestisci profilo (preferenza notifiche email e immagine del profilo)
  UC-16 – Logout

La dashboard e' una rotta protetta: il controllo accessi viene esercitato
prima dei flussi funzionali.

UC-15 copre:
  - la pagina del profilo e' raggiungibile solo da un utente autenticato;
  - il form del profilo e le liste (report personali, notifiche) sono visibili;
  - la preferenza "notifiche email" puo' essere modificata, salvata e persiste
    dopo un nuovo caricamento della pagina (poi viene ripristinata);
  - una nuova immagine del profilo puo' essere caricata e salvata;
  - i campi obbligatori del profilo bloccano il salvataggio se vuoti;
  - il pulsante di eliminazione account apre una conferma (qui annullata per
    mantenere ripetibile il seed).

UC-16 copre:
  - il logout reindirizza fuori dall'area autenticata e mostra di nuovo i link
    di login/registrazione;
  - dopo il logout una rotta protetta non e' piu' accessibile.
"""

import os
import tempfile

import pytest
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL


CITIZEN_EMAIL = "citizen@example.com"
CITIZEN_PASSWORD = "Citizen123!"

# Tempo di attesa generoso: l'ambiente di esecuzione puo' essere lento e ogni
# test esegue un login completo seguito da chiamate asincrone al backend.
WAIT = 20


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_temp_image(suffix: str = ".jpg") -> str:
    """Crea un file immagine JPEG minimale valido su disco e ne ritorna il path."""
    minimal_jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
        b"\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
        b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa"
        b"\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br"
        b"\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZ"
        b"cdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95"
        b"\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3"
        b"\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca"
        b"\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7"
        b"\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa"
        b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd4P\x00\x00\x00\x1f\xff\xd9"
    )
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as fh:
        fh.write(minimal_jpeg)
    return path


def _type(driver, element, value: str) -> None:
    """Svuota un campo in modo robusto e vi scrive `value`.

    Il semplice .clear() a volte non azzera il campo (bug noto del login, che
    finisce per concatenare la password): qui forzo selezione totale + cancella.
    """
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.DELETE)
    element.clear()
    element.send_keys(value)


def _login(driver, email: str, password: str, attempts: int = 3) -> None:
    """Login resiliente: riprova se si resta sulla pagina di login."""
    last_error = None
    for _ in range(attempts):
        driver.get(f"{BASE_URL}/login")
        ident = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.ID, "login-identifier"))
        )
        _type(driver, ident, email)
        _type(driver, driver.find_element(By.ID, "login-password"), password)
        driver.find_element(By.ID, "login-submit").click()
        try:
            WebDriverWait(driver, WAIT).until(lambda d: "/login" not in d.current_url)
            return
        except TimeoutException as exc:
            last_error = exc
    raise last_error


def _open_dashboard_as_citizen(driver) -> None:
    """Effettua il login come cittadino e attende il caricamento della dashboard."""
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "dashboard-page"))
    )


def _restore_email_notifications(driver, target_state: bool) -> None:
    """Riporta la preferenza notifiche email del cittadino a `target_state`.

    Best-effort: usato in un blocco finally per non lasciare il seed modificato;
    eventuali errori di ripristino non devono mascherare il fallimento del test.
    """
    try:
        driver.get(f"{BASE_URL}/dashboard")
        checkbox = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.ID, "profile-email-notifications"))
        )
        if checkbox.is_selected() != target_state:
            checkbox.click()
            driver.find_element(By.ID, "profile-save").click()
            WebDriverWait(driver, WAIT).until(
                EC.presence_of_element_located((By.ID, "profile-success"))
            )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Controllo accessi (UC-15 / UC-16 – precondizione: utente autenticato)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_dashboard_requires_authentication(driver):
    """Un visitatore non autenticato viene reindirizzato al login."""
    driver.get(f"{BASE_URL}/dashboard")
    WebDriverWait(driver, WAIT).until(lambda d: "/login" in d.current_url)
    assert "/login" in driver.current_url, (
        "La dashboard e' protetta: un utente non autenticato deve finire su /login"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Struttura della pagina
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_dashboard_page_loads_for_citizen(driver):
    """La dashboard mostra form del profilo, report personali e notifiche."""
    _open_dashboard_as_citizen(driver)

    # Elementi sempre visibili (hanno contenuto/dimensione non nulla).
    for element_id in (
        "profile-section",
        "profile-form",
        "profile-username",
        "profile-first-name",
        "profile-last-name",
        "profile-email",
        "profile-email-notifications",
        "profile-picture",
        "profile-save",
        "delete-account-button",
        "my-reports-card",
        "my-reports-table",
        "notifications-card",
        "notifications-title",
    ):
        assert driver.find_element(By.ID, element_id).is_displayed(), (
            f"L'elemento '{element_id}' deve essere visibile nella dashboard"
        )

    # La lista notifiche e' un contenitore che resta vuoto se non ci sono
    # notifiche (un <ul> vuoto ha altezza zero): qui basta che esista nel DOM.
    assert driver.find_element(By.ID, "notifications-list"), (
        "La lista notifiche deve essere presente nella dashboard"
    )

    # Il campo email e' di sola lettura (gestito dal sistema, non modificabile).
    assert driver.find_element(By.ID, "profile-email").get_attribute("readonly"), (
        "Il campo email del profilo deve essere di sola lettura"
    )


@pytest.mark.e2e
def test_dashboard_lists_seeded_citizen_reports(driver):
    """La tabella 'My reports' elenca le segnalazioni del cittadino (dati seed).

    Richiede che il backend sia stato avviato con i dati demo (seed). Le
    segnalazioni vengono caricate in modo asincrono dopo il render della pagina,
    quindi si attende esplicitamente la comparsa delle righe.
    """
    _open_dashboard_as_citizen(driver)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "my-reports-table-body"))
    )
    rows = WebDriverWait(driver, WAIT).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "tr[id^='my-report-row-']")
        )
    )
    assert rows, "La dashboard del cittadino deve elencare almeno una segnalazione del seed"
    assert "Damaged bench near school" in driver.page_source, (
        "La segnalazione seed del cittadino deve comparire nella dashboard"
    )


# ─────────────────────────────────────────────────────────────────────────────
# UC-15 – Gestisci profilo
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc15_email_notifications_preference_can_be_saved(driver):
    """UC-15: la preferenza notifiche email puo' essere salvata e persiste.

    Lo stato iniziale viene ripristinato al termine per mantenere il test
    ripetibile sull'account seed.
    """
    _open_dashboard_as_citizen(driver)
    checkbox = driver.find_element(By.ID, "profile-email-notifications")
    original_state = checkbox.is_selected()

    try:
        # Inverte la preferenza e salva.
        checkbox.click()
        new_state = checkbox.is_selected()
        assert new_state != original_state, "Il click deve invertire la preferenza"
        driver.find_element(By.ID, "profile-save").click()
        save_success = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "profile-success"))
        )
        assert "Profile updated." in save_success.text, (
            "Il salvataggio del profilo deve confermare con un messaggio di successo"
        )

        # Ricarica la pagina: la preferenza salvata deve persistere.
        driver.get(f"{BASE_URL}/dashboard")
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "dashboard-page"))
        )
        reloaded = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "profile-email-notifications"))
        )
        WebDriverWait(driver, WAIT).until(
            lambda d: d.find_element(By.ID, "profile-email-notifications").is_selected() == new_state
        )
        assert reloaded.is_selected() == new_state, (
            "La preferenza notifiche email salvata deve persistere dopo il ricaricamento"
        )
    finally:
        # Ripristino garantito dello stato seed originale, anche in caso di errore.
        _restore_email_notifications(driver, original_state)


@pytest.mark.e2e
def test_uc15_profile_picture_upload_succeeds(driver):
    """UC-15: il caricamento di una nuova immagine del profilo va a buon fine."""
    photo_path = _make_temp_image()
    try:
        _open_dashboard_as_citizen(driver)
        driver.find_element(By.ID, "profile-picture").send_keys(photo_path)
        driver.find_element(By.ID, "profile-save").click()
        success = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "profile-success"))
        )
        assert "Profile updated." in success.text, (
            "Dopo il salvataggio dell'immagine deve comparire il messaggio di conferma"
        )
    finally:
        os.unlink(photo_path)


@pytest.mark.e2e
def test_uc15_required_profile_field_blocks_save(driver):
    """UC-15: svuotare un campo obbligatorio del profilo blocca il salvataggio."""
    _open_dashboard_as_citizen(driver)
    username = driver.find_element(By.ID, "profile-username")
    username.clear()
    driver.find_element(By.ID, "profile-save").click()

    # L'attributo HTML `required` impedisce l'invio: nessun messaggio di successo.
    assert "/dashboard" in driver.current_url
    assert not driver.find_elements(By.ID, "profile-success"), (
        "Con lo username vuoto il profilo non deve essere salvato"
    )


@pytest.mark.e2e
def test_uc15_delete_account_confirmation_can_be_dismissed(driver):
    """UC-15: il pulsante elimina account apre una conferma; qui viene annullata.

    Annullare evita di distruggere l'account seed e mantiene la suite ripetibile.
    """
    _open_dashboard_as_citizen(driver)
    driver.find_element(By.ID, "delete-account-button").click()

    alert = WebDriverWait(driver, WAIT).until(EC.alert_is_present())
    assert alert.text, "L'eliminazione dell'account deve richiedere una conferma esplicita"
    alert.dismiss()

    # Annullata la conferma, l'utente resta sulla dashboard con la sessione attiva.
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        pytest.fail("La conferma non doveva ripresentarsi dopo l'annullamento")
    except (NoAlertPresentException, Exception):
        pass
    assert driver.find_element(By.ID, "dashboard-page").is_displayed()


# ─────────────────────────────────────────────────────────────────────────────
# UC-16 – Logout
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc16_logout_redirects_out_of_authenticated_area(driver):
    """UC-16: il logout termina la sessione e riporta i link di login/registrazione."""
    _open_dashboard_as_citizen(driver)
    driver.find_element(By.ID, "logout-button").click()

    # La dashboard e' protetta: senza sessione si viene reindirizzati al login.
    WebDriverWait(driver, WAIT).until(lambda d: "/dashboard" not in d.current_url)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "nav-login"))
    )
    assert "/dashboard" not in driver.current_url
    assert driver.find_element(By.ID, "nav-register").is_displayed()
    assert not driver.find_elements(By.ID, "logout-button"), (
        "Dopo il logout il pulsante di logout non deve essere visibile"
    )


@pytest.mark.e2e
def test_uc16_logout_blocks_protected_route(driver):
    """UC-16: dopo il logout una rotta protetta non e' piu' accessibile."""
    _open_dashboard_as_citizen(driver)
    driver.find_element(By.ID, "logout-button").click()
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "nav-login"))
    )

    driver.get(f"{BASE_URL}/dashboard")
    WebDriverWait(driver, WAIT).until(lambda d: "/login" in d.current_url)
    assert "/login" in driver.current_url, (
        "Senza sessione la dashboard deve reindirizzare al login"
    )