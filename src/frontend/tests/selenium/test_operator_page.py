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

def _create_report_via_ui(driver, title: str) -> str:
    """Crea una segnalazione come cittadino e ritorna l'ID estratto dall'URL."""
    _login(driver, CITIZEN_EMAIL, CITIZEN_PASSWORD)
    driver.get(f"{BASE_URL}/reports/new")
    
    img_path = _make_temp_image()
    try:
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "report-title"))).send_keys(title)
        driver.find_element(By.ID, "report-description").send_keys("Automated test description.")
        
        # Seleziona esplicitamente la categoria dell'operatore per evitare mismatch
        category_select = Select(driver.find_element(By.ID, "report-category"))
        category_select.select_by_visible_text("Roads and Urban Furniture")
        
        driver.find_element(By.ID, "report-photos").send_keys(img_path)
        driver.find_element(By.ID, "new-report-submit").click()
        
        # Aspetta il redirect alla pagina di dettaglio
        WebDriverWait(driver, WAIT).until(lambda d: "/reports/" in d.current_url and "/new" not in d.current_url)
        
        # Estrai ID dall'URL
        url_parts = driver.current_url.rstrip('/').split('/')
        report_id = url_parts[-1].split('?')[0]
        
        # Logout
        driver.get(f"{BASE_URL}/dashboard")
        WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, "logout-button"))).click()
        return report_id
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)

# ─────────────────────────────────────────────────────────────────────────────
# UC-10 – Gestisci segnalazione
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc10_operator_workflow(driver):
    """Test completo UC-10: assegnazione, aggiornamento stato e note."""
    unique_title = f"UC10 Test {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    # Login come operatore
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    
    # 1. Assegnazione (Pending -> Assigned)
    pending_row_id = f"pending-report-row-{report_id}"
    assign_btn_id = f"pending-report-assign-{report_id}"
    
    try:
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, pending_row_id)))
        assign_btn = driver.find_element(By.ID, assign_btn_id)
        try:
            assign_btn.click()
        except:
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
    
    # Attesa per il completamento della richiesta POST asincrona prima di navigare o rinfrescare.
    # Necessaria perché la UI non mostra un indicatore di caricamento o disabilita il bottone durante l'invio.
    time.sleep(2)

    # Verifica persistenza dopo refresh
    driver.refresh()
    
    # Verifica che lo stato sia corretto nella riga della tabella
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
    driver.get(f"{BASE_URL}/reports/new")
    
    img_path = _make_temp_image()
    try:
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "report-title"))).send_keys(unique_title)
        driver.find_element(By.ID, "report-description").send_keys("Test per isolamento categorie.")
        
        # Scegliamo una categoria diversa da quella dell'operatore seed ("Roads and Urban Furniture")
        category_select = Select(driver.find_element(By.ID, "report-category"))
        category_select.select_by_visible_text("Waste")
        
        driver.find_element(By.ID, "report-photos").send_keys(img_path)
        driver.find_element(By.ID, "new-report-submit").click()
        
        WebDriverWait(driver, WAIT).until(lambda d: "/reports/" in d.current_url and "/new" not in d.current_url)
    finally:
        if os.path.exists(img_path):
            os.unlink(img_path)

    # Logout cittadino
    driver.get(f"{BASE_URL}/dashboard")
    WebDriverWait(driver, WAIT).until(EC.element_to_be_clickable((By.ID, "logout-button"))).click()

    # 2. Login come operatore (assegnato a "Roads and Urban Furniture")
    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    
    # 3. Verifichiamo che le segnalazioni di altre categorie NON compaiano nella tabella pendenti
    try:
        # Aspettiamo un attimo per dare il tempo alla tabella di caricarsi se ci sono altri pendenti
        time.sleep(2)
        page_content = driver.page_source
        assert unique_title not in page_content, (
            "Errore Isolamento: L'operatore vede una segnalazione di una categoria non sua!"
        )
    except TimeoutException:
        pass # Va bene se la tabella dei pendenti non compare affatto (se non ha pendenti)

@pytest.mark.e2e
def test_uc10_rejection_requires_note(driver):
    """Test UC-10 Edge Case: Il rifiuto di una segnalazione fallisce se manca la nota."""
    unique_title = f"Reject Test {int(time.time())}"
    report_id = _create_report_via_ui(driver, unique_title)

    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    
    # 1. Assegnazione
    pending_row_id = f"pending-report-row-{report_id}"
    assign_btn_id = f"pending-report-assign-{report_id}"
    
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, pending_row_id)))
    assign_btn = driver.find_element(By.ID, assign_btn_id)
    try:
        assign_btn.click()
    except:
        driver.execute_script("arguments[0].click();", assign_btn)

    # 2. Tentativo di Rifiuto senza nota
    assigned_row_id = f"assigned-report-row-{report_id}"
    WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, assigned_row_id)))

    # Seleziona 'Rejected'
    status_select = Select(driver.find_element(By.ID, f"assigned-report-status-{report_id}"))
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

    _login(driver, OPERATOR_EMAIL, OPERATOR_PASSWORD)
    driver.get(f"{BASE_URL}/operator")
    
    # Assegna
    pending_assign_btn_id = f"pending-report-assign-{report_id}"
    assigned_row_id = f"assigned-report-row-{report_id}"
    
    # Se non è già assegnato, assegnalo
    try:
        assign_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, pending_assign_btn_id)))
        driver.execute_script("arguments[0].click();", assign_btn)
    except TimeoutException:
        # Forse è già assegnato da un'esecuzione precedente o seeding
        pass

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
    
    assert msg_body in driver.page_source
