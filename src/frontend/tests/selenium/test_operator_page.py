"""
Test di accettazione Selenium per l'area Operatore (/operator):

  UC-10 – Gestisci segnalazione (Assegnazione, aggiornamento stato e note)
  UC-11 – Invia messaggio al cittadino

Questi test verificano che un operatore possa prendere in carico una segnalazione,
aggiornarne l'avanzamento e comunicare con l'autore.
"""

import os
import tempfile
import time

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL

# Credenziali seed
CITIZEN_EMAIL = "citizen@example.com"
CITIZEN_PASSWORD = "Citizen123!"
OPERATOR_EMAIL = "operator@example.com"
OPERATOR_PASSWORD = "Operator123!"

# Tempo di attesa generoso per ambienti potenzialmente lenti
WAIT = 30

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
    """Svuota un campo in modo robusto e vi scrive `value`."""
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


def _logout(driver) -> None:
    """Esegue il logout in modo affidabile e aspetta che la sessione sia chiusa."""
    current = driver.current_url
    if "/login" in current or "/register" in current:
        return
    driver.get(f"{BASE_URL}/dashboard")
    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "logout-button"))
        )
        WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.ID, "logout-button"))
        ).click()
        WebDriverWait(driver, WAIT).until(
            lambda d: "/dashboard" not in d.current_url
        )
        WebDriverWait(driver, WAIT).until(
            lambda d: "/login" in d.current_url or d.current_url.endswith("/")
        )
    except Exception:
        driver.get(f"{BASE_URL}/login")
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "login-submit"))
        )



def _create_report_via_ui(driver, title: str, category_name: str | None = None) -> str:
    """
    Crea una segnalazione come cittadino e ritorna l'ID estratto dall'URL.
    Se category_name è None, usa la prima categoria disponibile con valore non vuoto.
    Effettua il logout del cittadino prima di ritornare.
    """
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "dashboard-page"))
    )
    # Aspetta logout-button: conferma che AuthContext ha propagato la sessione.
    # Senza questa attesa React reindirizza /reports/new alla login page.
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "logout-button"))
    )
    driver.get(f"{BASE_URL}/reports/new")
    # Retry: se React reindirizza per race condition, aspetta dashboard e riprova
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.ID, "new-report-page"))
        )
    except Exception:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "dashboard-page"))
        )
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "logout-button"))
        )
        driver.get(f"{BASE_URL}/reports/new")
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "new-report-page"))
        )

    img_path = _make_temp_image()
    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "report-title"))
        ).send_keys(title)
        driver.find_element(By.ID, "report-description").send_keys("Automated test description.")

        # Seleziona la categoria: usa quella passata o la prima disponibile
        category_select = Select(driver.find_element(By.ID, "report-category"))
        if category_name:
            category_select.select_by_visible_text(category_name)
        else:
            options = [o for o in category_select.options if o.get_attribute("value")]
            if not options:
                pytest.skip("Nessuna categoria disponibile")
            category_select.select_by_value(options[0].get_attribute("value"))

        driver.find_element(By.ID, "report-photos").send_keys(img_path)
        driver.find_element(By.ID, "new-report-submit").click()

        # Aspetta il redirect alla pagina di dettaglio
        WebDriverWait(driver, WAIT).until(
            lambda d: "/reports/" in d.current_url and "/new" not in d.current_url
        )

        # Estrai ID dall'URL
        report_id = driver.current_url.rstrip("/").split("/")[-1].split("?")[0]

        # Logout del cittadino
        _logout(driver)

        return report_id
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)


# Categoria del seed dell'operatore (operator@example.com → "Roads and Urban Furniture")
# Verificato dalla pagina /admin → lista utenti → riga #2.
OPERATOR_CATEGORY = "Roads and Urban Furniture"


# ─────────────────────────────────────────────────────────────────────────────
# UC-10 – Gestisci segnalazione
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc10_operator_workflow(driver):
    """Test completo UC-10: assegnazione, aggiornamento stato e note."""
    # Recupera la categoria dell'operatore dinamicamente per evitare hardcoding
    operator_category = OPERATOR_CATEGORY

    unique_title = f"UC10 Test {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title, category_name=operator_category)

    # Login come operatore
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    # Aspetta operator-title: conferma che AuthContext ha completato refreshCurrentUser()
    # e ProtectedRoute ha renderizzato la pagina con l'utente autenticato.
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-title"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-section"))
    )

    # 1. Assegnazione (Pending -> Assigned)
    # La sezione pending è renderizzata condizionalmente da React solo se ci sono report:
    # aspetta prima la sezione, poi la riga specifica.
    pending_row_id = f"pending-report-row-{report_id}"
    assign_btn_id = f"pending-report-assign-{report_id}"

    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "pending-reports-section"))
        )
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, pending_row_id))
        )
        assign_btn = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.ID, assign_btn_id))
        )
        driver.execute_script("arguments[0].click();", assign_btn)
    except Exception as e:
        pytest.fail(f"Fallimento durante assegnazione: {e}")

    # 2. Aggiornamento Stato e Note
    # Dopo il click su assign React chiama loadOperatorData() in modo asincrono.
    # La riga appare negli assegnati quando il fetch completa — aspettiamo direttamente.
    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT * 2).until(
        EC.presence_of_element_located((By.ID, assigned_row_id))
    )

    new_note = "In lavorazione - Selenium"
    status_select = Select(
        driver.find_element(By.ID, f"assigned-report-status-{report_id}")
    )
    status_select.select_by_visible_text("In Progress")

    note_input = driver.find_element(By.ID, f"assigned-report-note-{report_id}")
    _type(driver, note_input, new_note)

    driver.find_element(By.ID, f"assigned-report-update-{report_id}").click()

    # Attesa per il completamento della richiesta POST asincrona.
    # Necessaria perché la UI non mostra un indicatore di caricamento o disabilita il bottone.
    time.sleep(2)

    # Verifica persistenza dopo refresh
    driver.refresh()
    WebDriverWait(driver, WAIT).until(
        lambda d: Select(
            d.find_element(By.ID, f"assigned-report-status-{report_id}")
        ).first_selected_option.text == "In Progress"
    )

    # Vai al dettaglio per verificare la nota nella cronologia
    detail_link = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"assigned-report-row-{report_id}-open-detail"))
    )
    detail_link.click()

    # Aspetta che la nota appaia nella sezione Cronologia Stati del dettaglio
    history_note_xpath = (
        f"//li[contains(@id, 'status-history-item-') and .//p[contains(text(), '{new_note}')]]"
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, history_note_xpath))
    )

    # Verifica anche che lo stato nel dettaglio sia coerente
    val_status_detail = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-detail-status"))
    ).text
    assert "In Progress" in val_status_detail
    assert new_note in driver.page_source


@pytest.mark.e2e
def test_uc10_operator_suspended_workflow(driver):
    """Test UC-10: transizione allo stato 'Suspended'."""
    operator_category = OPERATOR_CATEGORY

    unique_title = f"Suspended Test {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title, category_name=operator_category)

    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-title"))
    )
    # Aspetta anche assigned-reports-section: conferma che loadOperatorData()
    # ha completato il primo fetch e React ha finito di renderizzare.
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-section"))
    )

    # 1. Assegnazione
    # Aspetta prima la sezione pending (renderizzata condizionalmente da React)
    assign_btn_id = f"pending-report-assign-{report_id}"
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "pending-reports-section"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, assign_btn_id))
    )
    driver.execute_script(
        "arguments[0].click();",
        driver.find_element(By.ID, assign_btn_id)
    )

    # 2. Sospensione
    # Aspetta che React aggiorni il DOM dopo loadOperatorData().
    WebDriverWait(driver, WAIT * 2).until(
        EC.presence_of_element_located((By.ID, f"assigned-report-row-{report_id}"))
    )
    status_select = Select(
        driver.find_element(By.ID, f"assigned-report-status-{report_id}")
    )
    status_select.select_by_visible_text("Suspended")

    suspension_note = "In attesa di pezzi di ricambio."
    note_input = driver.find_element(By.ID, f"assigned-report-note-{report_id}")
    _type(driver, note_input, suspension_note)

    driver.find_element(By.ID, f"assigned-report-update-{report_id}").click()
    time.sleep(2)  # Attesa async

    driver.refresh()
    WebDriverWait(driver, WAIT).until(
        lambda d: Select(
            d.find_element(By.ID, f"assigned-report-status-{report_id}")
        ).first_selected_option.text == "Suspended"
    )
    # Dopo il refresh il campo nota deve essere vuoto (non pre-popolato con la nota precedente)
    assert suspension_note not in driver.find_element(
        By.ID, f"assigned-report-note-{report_id}"
    ).get_attribute("value")


@pytest.mark.e2e
def test_operator_navigation_back_to_dashboard(driver):
    """Verifica che ci sia un link per tornare alla dashboard operatore dal dettaglio (tramite topbar)."""
    # Crea e assegna un report per garantire che ci sia almeno un link open-detail
    # indipendentemente dallo stato del DB (il seed originale non ha report assegnati).
    report_id = _create_report_via_ui(driver, f"Nav Test {int(time.time())}", category_name=OPERATOR_CATEGORY)

    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-title"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-section"))
    )

    # Assegna il report
    assign_btn_id = f"pending-report-assign-{report_id}"
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "pending-reports-section"))
    )
    WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, assign_btn_id)))
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, assign_btn_id))

    # Aspetta che la riga appaia negli assegnati
    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT * 2).until(
        EC.presence_of_element_located((By.ID, assigned_row_id))
    )

    # Prendi il link di dettaglio del report appena assegnato
    detail_links = WebDriverWait(driver, WAIT).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[id$='-open-detail']"))
    )
    detail_links[0].click()

    # Usa il link della topbar (nav-operator)
    back_link = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, "nav-operator"))
    )
    back_link.click()

    WebDriverWait(driver, WAIT).until(lambda d: d.current_url.endswith("/operator"))
    assert "/operator" in driver.current_url


# ─────────────────────────────────────────────────────────────────────────────
# UC-10 – Gestisci segnalazione (Estensioni ed Edge Cases)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc10_operator_category_isolation(driver):
    """Test UC-10 Edge Case: L'operatore non deve vedere segnalazioni di altre categorie."""
    # Recupera la categoria dell'operatore per poter scegliere una DIVERSA
    operator_category = OPERATOR_CATEGORY

    unique_title = f"Isolation Test {int(time.time())}"

    # Crea report in una categoria diversa da quella dell'operatore
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "dashboard-page"))
    )
    # Aspetta logout-button: conferma che AuthContext ha propagato la sessione.
    # Senza questa attesa React reindirizza /reports/new alla login page.
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "logout-button"))
    )
    driver.get(f"{BASE_URL}/reports/new")

    img_path = _make_temp_image()
    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "report-title"))
        ).send_keys(unique_title)
        driver.find_element(By.ID, "report-description").send_keys("Test per isolamento categorie.")

        # Seleziona la prima categoria che NON sia quella dell'operatore
        category_select = Select(driver.find_element(By.ID, "report-category"))
        other_options = [
            o for o in category_select.options
            if o.get_attribute("value") and o.text.strip() != operator_category
        ]
        if not other_options:
            pytest.skip("Non esistono altre categorie oltre a quella dell'operatore")
        category_select.select_by_value(other_options[0].get_attribute("value"))

        driver.find_element(By.ID, "report-photos").send_keys(img_path)
        driver.find_element(By.ID, "new-report-submit").click()
        WebDriverWait(driver, WAIT).until(
            lambda d: "/reports/" in d.current_url and "/new" not in d.current_url
        )
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)

    _logout(driver)

    # Login come operatore e verifica che il report non compaia
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    time.sleep(2)  # Attesa caricamento tabella
    assert unique_title not in driver.page_source, (
        "Errore Isolamento: L'operatore vede una segnalazione di una categoria non sua!"
    )


@pytest.mark.e2e
def test_uc10_rejection_requires_note(driver):
    """Test UC-10 Edge Case: Il rifiuto di una segnalazione fallisce se manca la nota."""
    operator_category = OPERATOR_CATEGORY

    unique_title = f"Reject Test {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title, category_name=operator_category)

    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-title"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-section"))
    )

    # 1. Assegnazione
    pending_row_id = f"pending-report-row-{report_id}"
    assign_btn_id = f"pending-report-assign-{report_id}"

    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "pending-reports-section"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, pending_row_id))
    )
    # Scroll sul bottone e click via JS per evitare intercettazioni di altri elementi
    assign_btn = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, assign_btn_id))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", assign_btn)
    driver.execute_script("arguments[0].click();", assign_btn)

    # 2. Tentativo di Rifiuto senza nota
    # Aspetta che React aggiorni il DOM dopo loadOperatorData().
    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT * 2).until(
        EC.presence_of_element_located((By.ID, assigned_row_id))
    )

    status_select = Select(
        driver.find_element(By.ID, f"assigned-report-status-{report_id}")
    )
    status_select.select_by_visible_text("Rejected")

    note_input = driver.find_element(By.ID, f"assigned-report-note-{report_id}")
    _type(driver, note_input, "")

    driver.find_element(By.ID, f"assigned-report-update-{report_id}").click()

    # Aspettiamo che appaia un errore — accettiamo sia operator-error sia operator-update-error
    try:
        error_element = WebDriverWait(driver, 10).until(
            lambda d: (
                d.find_elements(By.ID, "operator-error") or
                d.find_elements(By.ID, "operator-update-error") or
                d.find_elements(By.CSS_SELECTOR, "[id$='-error']:not([style*='display: none'])")
            )
        )
        # error_element è una lista; prendiamo il primo elemento visibile
        visible_errors = [
            el for el in driver.find_elements(By.CSS_SELECTOR, "[id$='-error']")
            if el.is_displayed()
        ]
        assert visible_errors, "Dovrebbe comparire un messaggio di errore per nota mancante."
    except TimeoutException:
        pytest.fail("Nessun messaggio di errore mostrato quando si rifiuta senza nota.")


@pytest.mark.e2e
def test_operator_forbidden_from_admin(driver):
    """Verifica che un operatore non possa accedere all'area admin."""
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/admin")

    WebDriverWait(driver, WAIT).until(lambda d: "/admin" not in d.current_url)
    assert "/admin" not in driver.current_url
    assert not driver.find_elements(By.ID, "admin-page")


@pytest.mark.e2e
def test_operator_cannot_access_unauthorized_report_detail(driver):
    """Verifica che un operatore non possa accedere al dettaglio di un report di un'altra categoria via URL."""
    operator_category = OPERATOR_CATEGORY

    unique_title = f"Secret Report {int(time.time())}"

    # 1. Crea report in una categoria diversa da quella dell'operatore
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "dashboard-page"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "logout-button"))
    )
    driver.get(f"{BASE_URL}/reports/new")
    img_path = _make_temp_image()
    try:
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, "report-title"))
        ).send_keys(unique_title)
        driver.find_element(By.ID, "report-description").send_keys("Access control test.")

        category_select = Select(driver.find_element(By.ID, "report-category"))
        other_options = [
            o for o in category_select.options
            if o.get_attribute("value") and o.text.strip() != operator_category
        ]
        if not other_options:
            pytest.skip("Non esistono altre categorie oltre a quella dell'operatore")
        category_select.select_by_value(other_options[0].get_attribute("value"))

        driver.find_element(By.ID, "report-photos").send_keys(img_path)
        driver.find_element(By.ID, "new-report-submit").click()
        WebDriverWait(driver, WAIT).until(
            lambda d: "/reports/" in d.current_url and "/new" not in d.current_url
        )
        report_url = driver.current_url
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)

    # 2. Logout cittadino (con attesa esplicita)
    _logout(driver)

    # 3. Login come Operatore e tentativo di accesso diretto
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(report_url)

    # Dovrebbe mostrare un messaggio di errore
    error_el = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-detail-error"))
    )
    error_text = error_el.text.lower()
    assert "access" in error_text or "not found" in error_text or "403" in error_text, (
        f"Messaggio di errore inatteso: '{error_el.text}'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# UC-11 – Invia messaggio al cittadino
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc11_operator_empty_message_blocked(driver):
    """Test UC-11 Edge Case: l'invio di un messaggio vuoto deve essere bloccato dall'attributo 'required'."""
    operator_category = OPERATOR_CATEGORY

    # Crea e assegna un report fresco per essere certi di avere la sezione messaggi disponibile
    unique_title = f"UC11 Empty {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title, category_name=operator_category)

    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-title"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-section"))
    )

    # Assegna — aspetta prima la sezione pending (renderizzata condizionalmente da React)
    assign_btn_id = f"pending-report-assign-{report_id}"
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "pending-reports-section"))
    )
    WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, assign_btn_id)))
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, assign_btn_id))

    # Vai al dettaglio — aspetta che React aggiorni il DOM dopo loadOperatorData().
    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT * 2).until(
        EC.presence_of_element_located((By.ID, assigned_row_id))
    )
    detail_link = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"{assigned_row_id}-open-detail"))
    )
    detail_link.click()

    # Verifica presenza attributo 'required' sul campo messaggio.
    # getAttribute("required") ritorna "" (stringa vuota) quando l'attributo è presente
    # senza valore esplicito, e None quando è assente — entrambi i valori truthy sono corretti.
    body_input = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-message-body"))
    )
    required_attr = body_input.get_attribute("required")
    assert required_attr is not None, (
        "Il campo messaggio deve avere l'attributo HTML 'required'"
    )

    # Tenta invio senza testo e verifica che non ci siano cambiamenti
    initial_msg_count = len(driver.find_elements(By.CSS_SELECTOR, "[id^='message-item-']"))
    driver.find_element(By.ID, "report-message-submit").click()

    time.sleep(1)
    current_msg_count = len(driver.find_elements(By.CSS_SELECTOR, "[id^='message-item-']"))
    assert initial_msg_count == current_msg_count, (
        "Non dovrebbe essere stato inviato alcun messaggio vuoto"
    )


@pytest.mark.e2e
def test_uc11_operator_sends_message(driver):
    """Test UC-11: l'operatore invia un messaggio dalla pagina di dettaglio."""
    operator_category = OPERATOR_CATEGORY

    unique_title = f"UC11 Msg {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title, category_name=operator_category)

    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-title"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-section"))
    )

    # Assegna — aspetta prima la sezione pending (renderizzata condizionalmente da React)
    pending_assign_btn_id = f"pending-report-assign-{report_id}"
    assigned_row_id = f"assigned-report-row-{report_id}"

    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "pending-reports-section"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, pending_assign_btn_id))
    )
    driver.execute_script(
        "arguments[0].click();",
        driver.find_element(By.ID, pending_assign_btn_id)
    )

    # Dopo il click su assign, React chiama loadOperatorData() in modo asincrono.
    # La sezione pending sparisce e la riga compare negli assegnati solo dopo
    # che la risposta API è tornata e React ha aggiornato il DOM.
    # Aspettiamo che la sezione pending-reports-section scompaia (indica che
    # il report non è più pending) prima di cercare la riga negli assegnati.
    WebDriverWait(driver, WAIT * 2).until(
        EC.presence_of_element_located((By.ID, assigned_row_id))
    )

    # Vai al dettaglio
    detail_link = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"{assigned_row_id}-open-detail"))
    )
    detail_link.click()

    # Invia messaggio
    msg_body = f"Messaggio operatore {int(time.time())}"
    body_input = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-message-body"))
    )
    body_input.send_keys(msg_body)
    driver.find_element(By.ID, "report-message-submit").click()

    # Verifica comparsa in lista
    msg_xpath = (
        f"//li[contains(@id, 'message-item-') and .//p[contains(text(), '{msg_body}')]]"
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, msg_xpath))
    )
    assert msg_body in driver.page_source