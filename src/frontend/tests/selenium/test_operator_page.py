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
WAIT = 20


# Vedi test_admin_page.py per la spiegazione completa: il backend usa una singola
# Connection SQLAlchemy globale + SessionLocal.remove() nel teardown_appcontext per
# ogni richiesta. Sotto richieste concorrenti questo produce "Authentication required"
# non deterministici. La race e' nel layer di connessione del backend, non nei test.
_BACKEND_AUTH_RACE_REASON = (
    "Backend shared global SQLAlchemy connection + per-request SessionLocal.remove() "
    "in teardown_appcontext causes non-deterministic 'Authentication required' under "
    "concurrent requests. Race is in the connection layer, not the test."
)

backend_auth_race = pytest.mark.xfail(reason=_BACKEND_AUTH_RACE_REASON, strict=False)

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

def _open_operator(driver) -> None:
    """Effettua il login come operatore e attende il caricamento della dashboard."""
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-page"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-table-body"))
    )


def _login_operator_and_open(driver) -> None:
    """Login operatore e apertura di /operator con la sessione gia' propagata.

    _login ritorna appena l'URL non e' piu' /login, ma la propagazione
    dell'AuthContext (e quindi del token usato dalle API) puo' non essere ancora
    completa. Navigare subito a /operator fa partire le fetch senza credenziali:
    la tabella resta vuota e le righe pending/assigned non compaiono mai, da cui
    i TimeoutException intermittenti. Si attende quindi il logout-button (presente
    solo a sessione autenticata attiva) prima di navigare alla rotta protetta.
    """
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "logout-button"))
    )
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "operator-page"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "assigned-reports-table-body"))
    )


def _select_category(driver, select_el, category_name: str) -> None:
    """Seleziona una categoria nel select e verifica che React abbia aggiornato lo stato."""
    target_value = None
    for opt in select_el.find_elements(By.TAG_NAME, "option"):
        if opt.text.strip() == category_name:
            target_value = opt.get_attribute("value")
            break
    if target_value is None:
        pytest.skip(f"Categoria '{category_name}' non trovata")
    Select(select_el).select_by_value(target_value)
    # Dispatch the change event explicitly so React 19 picks up the selection
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
        select_el,
    )
    # Wait until the DOM value matches — confirms React has committed the state update
    WebDriverWait(driver, WAIT).until(
        lambda d: d.find_element(By.ID, "report-category").get_attribute("value") == target_value
    )


def _create_report_via_ui(driver, title: str) -> str:
    """Crea una segnalazione come cittadino e ritorna l'ID estratto dall'URL."""
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    # Wait for dashboard + logout-button before navigating: confirms AuthContext has propagated
    # and prevents ProtectedRoute from redirecting /reports/new back to /login.
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "dashboard-page")))
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "logout-button")))
    driver.get(f"{BASE_URL}/reports/new")

    img_path = _make_temp_image()
    try:
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "new-report-form")))
        driver.find_element(By.ID, "report-title").send_keys(title)
        driver.find_element(By.ID, "report-description").send_keys("Automated test description.")

        # Wait for categories to load asynchronously
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#report-category option[value]"))
        )
        _select_category(driver, driver.find_element(By.ID, "report-category"), "Roads and Urban Furniture")

        driver.find_element(By.ID, "report-photos").send_keys(img_path)
        driver.find_element(By.ID, "new-report-submit").click()

        WebDriverWait(driver, WAIT).until(lambda d: "/reports/" in d.current_url and "/new" not in d.current_url)

        url_parts = driver.current_url.rstrip('/').split('/')
        report_id = url_parts[-1].split('?')[0]

        # Logout — wait for redirect to confirm session is closed
        driver.get(f"{BASE_URL}/dashboard")
        WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, "logout-button"))).click()
        WebDriverWait(driver, WAIT).until(lambda d: "/dashboard" not in d.current_url)
        return report_id
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)

# ─────────────────────────────────────────────────────────────────────────────
# Controllo accessi
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_operator_requires_authentication(driver):
    """Un visitatore non autenticato viene reindirizzato al login."""
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(lambda d: "/login" in d.current_url)
    assert "/login" in driver.current_url


@pytest.mark.e2e
def test_operator_forbidden_for_citizen(driver):
    """Un cittadino autenticato non può accedere alla dashboard operatore."""
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    WebDriverWait(driver, WAIT).until(lambda d: "/operator" not in d.current_url)
    assert "/operator" not in driver.current_url
    assert not driver.find_elements(By.ID, "operator-page")


# ─────────────────────────────────────────────────────────────────────────────
# Struttura della pagina
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_operator_page_loads_for_operator(driver):
    """La dashboard mostra il riepilogo, il titolo e la tabella dei report assegnati."""
    _open_operator(driver)
    for element_id in (
        "operator-summary-section",
        "operator-title",
        "assigned-reports-section",
        "assigned-reports-title",
        "assigned-reports-table",
        "assigned-reports-table-body",
    ):
        assert driver.find_element(By.ID, element_id).is_displayed(), (
            f"L'elemento '{element_id}' deve essere visibile nella dashboard operatore"
        )


# ─────────────────────────────────────────────────────────────────────────────
# UC-10 – Gestisci segnalazione
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc10_operator_workflow(driver):
    """Test completo UC-10: assegnazione, aggiornamento stato e note."""
    unique_title = f"UC10 Test {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    # Login come operatore (sessione propagata prima di navigare alla rotta protetta)
    _login_operator_and_open(driver)

    # 1. Assegnazione (Pending -> Assigned)
    pending_row_id = f"pending-report-row-{report_id}"
    assign_btn_id = f"pending-report-assign-{report_id}"

    try:
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, pending_row_id)))
        assign_btn = driver.find_element(By.ID, assign_btn_id)
        try:
            assign_btn.click()
        except Exception:
            driver.execute_script("arguments[0].click();", assign_btn)
    except Exception as e:
        pytest.fail(f"Fallimento durante assegnazione: {e}")

    # 2. Aggiornamento Stato e Note
    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, assigned_row_id)))

    new_note = "In lavorazione - Selenium"
    status_select = Select(driver.find_element(By.ID, f"assigned-report-status-{report_id}"))
    status_select.select_by_visible_text("In Progress")
    
    note_input = driver.find_element(By.ID, f"assigned-report-note-{report_id}")
    _type(driver, note_input, new_note)
    
    driver.find_element(By.ID, f"assigned-report-update-{report_id}").click()

    # Verifica persistenza dopo refresh
    driver.refresh()
    WebDriverWait(driver, WAIT).until(
        lambda d: Select(d.find_element(By.ID, f"assigned-report-status-{report_id}")).first_selected_option.text == "In Progress"
    )
    
    # Vai al dettaglio per verificare la nota nella cronologia (UC-10 richiede aggiornamento note)
    detail_link = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"assigned-report-row-{report_id}-open-detail"))
    )
    detail_link.click()

    # Aspetta che la nota appaia nella sezione Cronologia Stati del dettaglio
    history_note_xpath = f"//li[contains(@id, 'status-history-item-') and .//p[contains(text(), '{new_note}')]]"
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, history_note_xpath)))
    
    # Verifica anche che lo stato nel dettaglio sia coerente
    val_status_detail = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-detail-status"))
    ).text
    assert "In Progress" in val_status_detail
    assert new_note in driver.page_source

# ─────────────────────────────────────────────────────────────────────────────
# UC-10 – Gestisci segnalazione (Estensioni ed Edge Cases)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc10_operator_category_isolation(driver):
    """Test UC-10 Edge Case: L'operatore non deve vedere segnalazioni di altre categorie."""
    unique_title = f"Isolation Test {int(time.time())}"
    
    # 1. Creiamo un report in una categoria DIVERSA (es. "Waste")
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "dashboard-page")))
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "logout-button")))
    driver.get(f"{BASE_URL}/reports/new")

    img_path = _make_temp_image()
    try:
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "new-report-form")))
        driver.find_element(By.ID, "report-title").send_keys(unique_title)
        driver.find_element(By.ID, "report-description").send_keys("Test per isolamento categorie.")

        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#report-category option[value]"))
        )
        _select_category(driver, driver.find_element(By.ID, "report-category"), "Waste")

        driver.find_element(By.ID, "report-photos").send_keys(img_path)
        driver.find_element(By.ID, "new-report-submit").click()

        WebDriverWait(driver, WAIT).until(lambda d: "/reports/" in d.current_url and "/new" not in d.current_url)
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)

    # Logout cittadino — attende il redirect per garantire che la sessione sia chiusa
    driver.get(f"{BASE_URL}/dashboard")
    WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, "logout-button"))).click()
    WebDriverWait(driver, WAIT).until(lambda d: "/dashboard" not in d.current_url)

    # 2. Login come operatore (assegnato a "Roads and Urban Furniture")
    _login_operator_and_open(driver)

    # 3. Verifichiamo che le segnalazioni di altre categorie NON compaiano nella tabella pendenti
    assert unique_title not in driver.page_source, (
        "Errore isolamento: l'operatore vede una segnalazione di una categoria non sua"
    )

@pytest.mark.e2e
def test_uc10_rejection_requires_note(driver):
    """Test UC-10 Edge Case: Il rifiuto di una segnalazione fallisce se manca la nota."""
    unique_title = f"Reject Test {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    _login_operator_and_open(driver)

    # 1. Assegnazione
    pending_row_id = f"pending-report-row-{report_id}"
    assign_btn_id = f"pending-report-assign-{report_id}"

    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, pending_row_id)))
    assign_btn = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, assign_btn_id))
    )
    try:
        assign_btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", assign_btn)

    # 2. Tentativo di Rifiuto senza nota
    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, assigned_row_id)))

    # Seleziona 'Rejected' (attende che la select assegnata sia presente)
    status_select = Select(
        WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, f"assigned-report-status-{report_id}"))
        )
    )
    status_select.select_by_visible_text("Rejected")
    
    # Assicurati che la nota sia vuota
    note_input = driver.find_element(By.ID, f"assigned-report-note-{report_id}")
    _type(driver, note_input, "")
    
    driver.find_element(By.ID, f"assigned-report-update-{report_id}").click()
    
    # Aspettiamo che appaia l'errore globale della pagina operatore
    try:
        error_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "operator-error"))
        )
        assert error_element.is_displayed(), "Dovrebbe comparire un messaggio di errore per nota mancante."
    except TimeoutException:
        pytest.fail("Nessun messaggio di errore mostrato quando si rifiuta senza nota.")

# ─────────────────────────────────────────────────────────────────────────────
# UC-11 – Invia messaggio al cittadino
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc11_operator_sends_message(driver):
    """Test UC-11: l'operatore invia un messaggio dalla pagina di dettaglio."""
    unique_title = f"UC11 Msg {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    _login_operator_and_open(driver)

    # Assegna
    pending_assign_btn_id = f"pending-report-assign-{report_id}"
    assigned_row_id = f"assigned-report-row-{report_id}"

    # Assegna il report (appena creato, sempre in stato Pending)
    assign_btn = WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, pending_assign_btn_id)))
    driver.execute_script("arguments[0].click();", assign_btn)

    # Aspetta che appaia nella sezione assegnati
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, assigned_row_id)))

    # Vai al dettaglio
    detail_link = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"{assigned_row_id}-open-detail"))
    )
    detail_link.click()

    # Invia messaggio
    msg_body = f"Messaggio operatore {int(time.time())}"
    body_input = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "report-message-body")))
    body_input.send_keys(msg_body)
    driver.find_element(By.ID, "report-message-submit").click()

    # Verifica comparsa in lista
    msg_xpath = f"//li[contains(@id, 'message-item-') and .//p[contains(text(), '{msg_body}')]]"
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.XPATH, msg_xpath)))

# ─────────────────────────────────────────────────────────────────────────────
# UC-11 Extension 3a — corpo messaggio vuoto bloccato
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc11_empty_message_is_blocked(driver):
    """UC-11 Ext 3a: l'operatore non può inviare un messaggio con corpo vuoto."""
    unique_title = f"UC11 Empty {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    _login_operator_and_open(driver)

    assign_btn = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"pending-report-assign-{report_id}"))
    )
    driver.execute_script("arguments[0].click();", assign_btn)

    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, assigned_row_id))
    )
    WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"{assigned_row_id}-open-detail"))
    ).click()

    body_input = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-message-body"))
    )
    body_input.clear()

    msgs_before = len(driver.find_elements(By.CSS_SELECTOR, "li[id^='message-item-']"))

    driver.find_element(By.ID, "report-message-submit").click()

    # Esito atteso: nessun nuovo messaggio. Accettiamo due forme:
    #   (a) messaggio di errore visibile (ID report-message-error), oppure
    #   (b) il contatore messaggi resta invariato (validazione client).
    def _no_message_sent(d):
        err = d.find_elements(By.ID, "report-message-error")
        err_shown = bool(err) and err[0].is_displayed()
        msgs_now = len(d.find_elements(By.CSS_SELECTOR, "li[id^='message-item-']"))
        return err_shown or msgs_now == msgs_before

    WebDriverWait(driver, 10).until(_no_message_sent)

    msgs_after = len(driver.find_elements(By.CSS_SELECTOR, "li[id^='message-item-']"))
    assert msgs_after == msgs_before, (
        "Un messaggio con corpo vuoto non deve essere inviato "
        f"(messaggi prima={msgs_before}, dopo={msgs_after})"
    )


# ─────────────────────────────────────────────────────────────────────────────
# UC-12 — Reply to Municipal Operator message (lato cittadino)
# ─────────────────────────────────────────────────────────────────────────────

def _operator_sends_message_and_logout(driver, report_id: str, body: str) -> None:
    """Helper UC-12: come operatore assegnato, invia un messaggio sul report
    e fa logout. Lascia il driver sulla pagina di login (o home), pronto per
    il login del cittadino.

    Nota: NON naviga a /dashboard (rotta non accessibile all'operatore). Il
    logout è eseguito tramite il pulsante presente sulla pagina corrente.
    """
    _login_operator_and_open(driver)
    assign_btn = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"pending-report-assign-{report_id}"))
    )
    driver.execute_script("arguments[0].click();", assign_btn)

    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, assigned_row_id))
    )
    WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, f"{assigned_row_id}-open-detail"))
    ).click()

    body_input = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-message-body"))
    )
    body_input.send_keys(body)
    driver.find_element(By.ID, "report-message-submit").click()

    msg_xpath = f"//li[contains(@id, 'message-item-') and .//p[contains(text(), '{body}')]]"
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, msg_xpath))
    )

    # Logout dal dettaglio del report (senza navigare a /dashboard, inaccessibile
    # all'operatore): attende il bottone sulla pagina corrente e lo clicca.
    logout_btn = WebDriverWait(driver, WAIT).until(
        EC.element_to_be_clickable((By.ID, "logout-button"))
    )
    logout_btn.click()
    WebDriverWait(driver, WAIT).until(
        lambda d: not d.find_elements(By.ID, "logout-button")
    )


@pytest.mark.e2e
def test_uc12_citizen_replies_to_operator_message(driver):
    """UC-12: il cittadino risponde a un messaggio dell'operatore e la risposta
    appare nella conversazione del report."""
    unique_title = f"UC12 Reply {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    operator_msg = f"Domanda operatore {int(time.time())}"
    _operator_sends_message_and_logout(driver, report_id, operator_msg)

    # Login cittadino con sessione propagata prima di navigare al dettaglio.
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "dashboard-page"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "logout-button"))
    )
    driver.get(f"{BASE_URL}/reports/{report_id}")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-detail-page"))
    )

    # Il messaggio dell'operatore deve essere visibile (precondizione UC-12).
    op_msg_xpath = (
        f"//li[contains(@id, 'message-item-') and .//p[contains(text(), '{operator_msg}')]]"
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, op_msg_xpath))
    )

    # Compone e invia la risposta.
    reply_body = f"Risposta cittadino {int(time.time())}"
    body_input = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-message-body"))
    )
    body_input.send_keys(reply_body)
    driver.find_element(By.ID, "report-message-submit").click()

    reply_xpath = (
        f"//li[contains(@id, 'message-item-') and .//p[contains(text(), '{reply_body}')]]"
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.XPATH, reply_xpath))
    )
    assert reply_body in driver.page_source, (
        "La risposta del cittadino deve comparire nella conversazione del report"
    )


@pytest.mark.e2e
def test_uc12_citizen_empty_reply_is_blocked(driver):
    """UC-12 Ext 3a: una risposta con corpo vuoto non viene inviata."""
    unique_title = f"UC12 EmptyReply {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    operator_msg = f"Domanda operatore {int(time.time())}"
    _operator_sends_message_and_logout(driver, report_id, operator_msg)

    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "dashboard-page"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "logout-button"))
    )
    driver.get(f"{BASE_URL}/reports/{report_id}")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-detail-page"))
    )

    body_input = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "report-message-body"))
    )
    body_input.clear()

    msgs_before = len(driver.find_elements(By.CSS_SELECTOR, "li[id^='message-item-']"))
    driver.find_element(By.ID, "report-message-submit").click()

    def _no_reply_sent(d):
        err = d.find_elements(By.ID, "report-message-error")
        err_shown = bool(err) and err[0].is_displayed()
        msgs_now = len(d.find_elements(By.CSS_SELECTOR, "li[id^='message-item-']"))
        return err_shown or msgs_now == msgs_before

    WebDriverWait(driver, 10).until(_no_reply_sent)

    msgs_after = len(driver.find_elements(By.CSS_SELECTOR, "li[id^='message-item-']"))
    assert msgs_after == msgs_before, (
        "Una risposta vuota non deve essere inviata "
        f"(messaggi prima={msgs_before}, dopo={msgs_after})"
    )