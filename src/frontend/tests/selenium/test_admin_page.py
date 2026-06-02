"""
Test di accettazione Selenium per il pannello di amministrazione (/admin):

  UC-13 – Visualizza statistiche private
  UC-14 – Gestisci configurazione (categorie e account utente)

Il pannello admin e' una rotta protetta riservata al ruolo Administrator:
il controllo accessi viene esercitato prima dei flussi funzionali.

Convenzione marker (coerente con il resto della suite):
  - @pytest.mark.e2e            -> test affidabili, eseguiti con `pytest -m e2e`;
  - @pytest.mark.implementation_bug -> test che documentano un bug noto e che
    risultano instabili (qui: la categoria appena creata non compare in modo
    affidabile nella tabella delle categorie senza un refresh / re-login).

UC-13 copre:
  - la sezione statistiche e' visibile;
  - sono presenti le viste per stato, tipo/categoria, reporter e top reporter.

UC-14 copre:
  - solo l'amministratore puo' accedere alla configurazione;
  - i form di creazione e le tabelle di utenti e categorie sono visibili;
  - una nuova categoria puo' essere creata (messaggio di conferma);
  - Extension 4b: un nome di categoria duplicato mostra un errore;
  - una categoria esistente (seed) puo' essere aggiornata;
  - un nuovo utente / operatore con categoria puo' essere creato;
  - un utente esistente (seed) puo' essere aggiornato;
  - un'email gia' registrata blocca la creazione di un nuovo utente.

Nota su Extension 4a (cancellazione di una categoria usata da segnalazioni):
l'interfaccia di amministrazione espone l'aggiornamento/disattivazione delle
categorie, non la cancellazione definitiva; viene quindi verificata
l'aggiornamento di una categoria esistente.
"""

import time

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL


ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123!"

# Attesa generosa: ambiente potenzialmente lento + login completo per ogni test.
WAIT = 15


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _unique_suffix() -> str:
    return str(int(time.time() * 1000))


def _type(driver, element, value: str) -> None:
    """Svuota un campo in modo robusto e vi scrive `value` (mitiga il bug noto
    del login in cui .clear() non azzera e la password risulta concatenata)."""
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


def _open_admin(driver) -> None:
    """Effettua il login come amministratore e attende il pannello admin."""
    _login(driver, ADMIN_EMAIL, ADMIN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-page"))
    )
    # I dati admin sono caricati in modo asincrono: attende le tabelle popolate.
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-users-table-body"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-categories-table-body"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-statistics-section"))
    )


def _react_set_checkbox(driver, checkbox_element, checked: bool) -> None:
    """Aggiorna un checkbox React-controlled in modo affidabile in headless Chrome.

    Selenium's .click() non garantisce che l'onChange di React venga triggerato
    (la DOM si aggiorna ma React può resettarla prima del prossimo render).
    Il setter nativo + dispatchEvent è l'approccio standard React-testing.
    """
    driver.execute_script(
        "Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'checked')"
        ".set.call(arguments[0], arguments[1]);"
        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        checkbox_element,
        checked,
    )


def _create_category(driver, name: str) -> None:
    """Compila e invia il form di creazione categoria."""
    field = driver.find_element(By.ID, "admin-new-category-name")
    _type(driver, field, name)
    driver.find_element(By.ID, "admin-new-category-submit").click()


def _wait_admin_success(driver):
    """Attende il messaggio di successo admin."""
    try:
        element = WebDriverWait(driver, WAIT).until(
            lambda d: (
                d.find_elements(By.ID, "admin-success") and
                d.find_element(By.ID, "admin-success").text.strip()
            ) and d.find_element(By.ID, "admin-success")
        )
        return element
    except TimeoutException:
        errors = driver.find_elements(By.ID, "admin-error")
        detail = errors[0].text if errors else "nessun messaggio mostrato"
        raise AssertionError(
            f"Nessun messaggio di successo dopo il salvataggio. admin-error: {detail}"
        )


def _find_user_id_by_email(driver, email: str) -> str:
    """Ritorna l'ID UI dell'utente con l'email indicata, cercando tra le righe
    della tabella tramite il prefisso ID stabile `admin-user-email-`."""
    inputs = WebDriverWait(driver, WAIT).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "input[id^='admin-user-email-']")
        )
    )
    for field in inputs:
        if field.get_attribute("value") == email:
            return field.get_attribute("id").replace("admin-user-email-", "")
    raise AssertionError(f"Nessuna riga utente trovata per l'email '{email}'")


def _find_category_id_by_name(driver, name: str) -> str:
    """Ritorna l'ID UI della categoria con il nome indicato, tramite il prefisso
    ID stabile `admin-category-name-`."""
    inputs = WebDriverWait(driver, WAIT).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "input[id^='admin-category-name-']")
        )
    )
    for field in inputs:
        if field.get_attribute("value") == name:
            return field.get_attribute("id").replace("admin-category-name-", "")
    raise AssertionError(f"Nessuna riga categoria trovata per il nome '{name}'")


def _restore_category_active(driver, category_id: str, target_active: bool) -> None:
    """Riporta il flag attivo di una categoria al valore desiderato (best-effort)."""
    try:
        checkbox = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.ID, f"admin-category-active-{category_id}"))
        )
        if checkbox.is_selected() != target_active:
            checkbox.click()
            driver.find_element(By.ID, f"admin-category-save-{category_id}").click()
            WebDriverWait(driver, WAIT).until(
                EC.presence_of_element_located((By.ID, "admin-success"))
            )
    except Exception:
        pass


def _restore_user_email_notifications(driver, user_id: str, target_state: bool) -> None:
    """Riporta la preferenza notifiche email di un utente al valore desiderato (best-effort)."""
    try:
        checkbox = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.ID, f"admin-user-email-notifications-{user_id}"))
        )
        if checkbox.is_selected() != target_state:
            checkbox.click()
            driver.find_element(By.ID, f"admin-user-save-{user_id}").click()
            WebDriverWait(driver, WAIT).until(
                EC.presence_of_element_located((By.ID, "admin-success"))
            )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Controllo accessi (UC-13 / UC-14 – precondizione: ruolo Administrator)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_admin_requires_authentication(driver):
    """Un visitatore non autenticato viene reindirizzato al login."""
    driver.get(f"{BASE_URL}/admin")
    WebDriverWait(driver, WAIT).until(lambda d: "/login" in d.current_url)
    assert "/login" in driver.current_url


@pytest.mark.e2e
def test_admin_forbidden_for_citizen(driver):
    """Un cittadino autenticato non puo' accedere al pannello admin."""
    _login(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/admin")
    WebDriverWait(driver, WAIT).until(lambda d: "/admin" not in d.current_url)
    assert "/admin" not in driver.current_url, (
        "Un ruolo non admin deve essere reindirizzato fuori dal pannello admin"
    )
    assert not driver.find_elements(By.ID, "admin-page")


# ─────────────────────────────────────────────────────────────────────────────
# Struttura della pagina
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_admin_page_loads_for_admin(driver):
    """Il pannello admin mostra i form di creazione e le tabelle."""
    _open_admin(driver)
    for element_id in (
        "admin-summary-section",
        "admin-user-form",
        "admin-new-user-username",
        "admin-new-user-email",
        "admin-new-user-role",
        "admin-new-user-submit",
        "admin-category-form",
        "admin-new-category-name",
        "admin-new-category-submit",
        "admin-users-section",
        "admin-users-table",
        "admin-categories-section",
        "admin-categories-table",
        "admin-statistics-section",
    ):
        assert driver.find_element(By.ID, element_id).is_displayed(), (
            f"L'elemento '{element_id}' deve essere visibile nel pannello admin"
        )


# ─────────────────────────────────────────────────────────────────────────────
# UC-13 – Statistiche private
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc13_statistics_sections_visible(driver):
    """UC-13: sono visibili le statistiche per stato, tipo, reporter e top reporter."""
    _open_admin(driver)
    assert driver.find_element(By.ID, "admin-statistics-title").is_displayed()

    expected_metric_items = (
        "admin-metric-item-reports-by-status",
        "admin-metric-item-reports-by-type",
        "admin-metric-item-reports-by-reporter",
        "admin-metric-item-top-1-percent-by-type",
        "admin-metric-item-top-5-percent-by-type",
    )
    for metric_id in expected_metric_items:
        block = WebDriverWait(driver, WAIT).until(
            EC.presence_of_element_located((By.ID, metric_id))
        )
        assert block.is_displayed(), (
            f"La vista statistica '{metric_id}' deve essere visibile"
        )
        assert driver.find_element(By.ID, f"{metric_id}-title").is_displayed()


# ─────────────────────────────────────────────────────────────────────────────
# UC-14 – Gestisci configurazione: categorie
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc14_create_category_shows_success(driver):
    """UC-14: la creazione di una nuova categoria conferma con un messaggio di successo."""
    _open_admin(driver)
    name = f"Selenium Category {_unique_suffix()}"
    _create_category(driver, name)

    success = _wait_admin_success(driver)
    assert "Category created." in success.text, (
        "La creazione della categoria deve mostrare il messaggio di conferma"
    )


@pytest.mark.e2e
def test_uc14_create_duplicate_category_shows_error(driver):
    """UC-14 Extension 4b: un nome di categoria gia' esistente mostra un errore."""
    _open_admin(driver)
    # "Waste" e' una delle categorie di default nel seed.
    _create_category(driver, "Waste")
    error = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-error"))
    )
    assert error.is_displayed(), (
        "La creazione di una categoria con nome duplicato deve mostrare un errore"
    )


@pytest.mark.e2e
def test_uc14_update_existing_category_succeeds(driver):
    _open_admin(driver)
    category_id = _find_category_id_by_name(driver, "Other")

    try:
        active = driver.find_element(By.ID, f"admin-category-active-{category_id}")
        target = not active.is_selected()
        _react_set_checkbox(driver, active, target)
        WebDriverWait(driver, WAIT).until(
            lambda d: d.find_element(By.ID, f"admin-category-active-{category_id}").is_selected() == target
        )
        driver.execute_script(
            "arguments[0].click();",
            driver.find_element(By.ID, f"admin-category-save-{category_id}"),
        )

        # Aspetta che admin-success appaia con testo prima che loadAdminData lo sovrascriva
        success_text = WebDriverWait(driver, WAIT).until(
            lambda d: (
                d.find_elements(By.ID, "admin-success") and
                d.find_element(By.ID, "admin-success").text.strip()
            ) and d.find_element(By.ID, "admin-success").text.strip()
        )
        assert f"Category #{category_id} updated." in success_text, (
            f"Messaggio di successo inatteso: '{success_text}'"
        )
    finally:
        _restore_category_active(driver, category_id, target_active=True)


# ─────────────────────────────────────────────────────────────────────────────
# UC-14 – Gestisci configurazione: utenti
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc14_create_user_shows_success(driver):
    """UC-14: la creazione di un nuovo account cittadino conferma con un messaggio."""
    _open_admin(driver)
    suffix = _unique_suffix()
    email = f"selenium_user_{suffix}@example.com"

    driver.find_element(By.ID, "admin-new-user-username").send_keys(f"sel_user_{suffix}")
    driver.find_element(By.ID, "admin-new-user-first-name").send_keys("Selenium")
    driver.find_element(By.ID, "admin-new-user-last-name").send_keys("User")
    driver.find_element(By.ID, "admin-new-user-email").send_keys(email)
    driver.find_element(By.ID, "admin-new-user-password").send_keys("Test1234!")
    # referenceData (che popola il select ruoli) può arrivare dopo admin-statistics-section:
    # aspetta almeno un'opzione prima di tentare select_by_value.
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#admin-new-user-role option[value]"))
    )
    # Ruolo cittadino: nessuna categoria richiesta, flusso piu' deterministico.
    Select(driver.find_element(By.ID, "admin-new-user-role")).select_by_value("citizen")
    # Conferma che React abbia applicato il cambio di ruolo prima di inviare.
    WebDriverWait(driver, WAIT).until(
        lambda d: d.find_element(By.ID, "admin-new-user-role").get_attribute("value") == "citizen"
    )
    driver.find_element(By.ID, "admin-new-user-submit").click()

    success = _wait_admin_success(driver)
    assert "User created." in success.text, (
        "La creazione dell'utente deve mostrare il messaggio di conferma"
    )


@pytest.mark.e2e
def test_uc14_create_operator_with_category_shows_success(driver):
    """UC-14: la creazione di un operatore con categoria assegnata (caso centrale UC-14)."""
    _open_admin(driver)
    suffix = _unique_suffix()
    email = f"selenium_op_{suffix}@example.com"

    driver.find_element(By.ID, "admin-new-user-username").send_keys(f"sel_op_{suffix}")
    driver.find_element(By.ID, "admin-new-user-first-name").send_keys("Selenium")
    driver.find_element(By.ID, "admin-new-user-last-name").send_keys("Operator")
    driver.find_element(By.ID, "admin-new-user-email").send_keys(email)
    driver.find_element(By.ID, "admin-new-user-password").send_keys("Test1234!")
    Select(driver.find_element(By.ID, "admin-new-user-role")).select_by_value("operator")

    # Per un operatore la select categoria si abilita: seleziona la prima reale.
    category_select = Select(driver.find_element(By.ID, "admin-new-user-category"))
    real_options = [
        opt for opt in category_select.options if (opt.get_attribute("value") or "").strip()
    ]
    assert real_options, "Devono esistere categorie attive da assegnare all'operatore"
    category_select.select_by_value(real_options[0].get_attribute("value"))

    driver.find_element(By.ID, "admin-new-user-submit").click()
    success = _wait_admin_success(driver)
    assert "User created." in success.text, (
        "La creazione dell'operatore deve mostrare il messaggio di conferma"
    )


@pytest.mark.e2e
def test_uc14_update_existing_user_succeeds(driver):
    """UC-14: un account utente esistente del seed puo' essere modificato e salvato.

    Si agisce sull'operatore seed invertendo la preferenza notifiche email,
    poi si ripristina lo stato. La riga del seed e' sempre presente al load.
    """
    _open_admin(driver)
    user_id = _find_user_id_by_email(driver, "operator@example.com")

    flag = driver.find_element(By.ID, f"admin-user-email-notifications-{user_id}")
    original_state = flag.is_selected()

    try:
        target = not original_state
        _react_set_checkbox(driver, flag, target)
        WebDriverWait(driver, WAIT).until(
            lambda d: d.find_element(By.ID, f"admin-user-email-notifications-{user_id}").is_selected() == target
        )
        driver.execute_script(
            "arguments[0].click();",
            driver.find_element(By.ID, f"admin-user-save-{user_id}"),
        )

        success = _wait_admin_success(driver)
        assert f"User #{user_id} updated." in success.text, (
            "L'aggiornamento dell'utente deve mostrare il messaggio di conferma"
        )
    finally:
        # Ripristino garantito dello stato seed dell'operatore.
        _restore_user_email_notifications(driver, user_id, original_state)


@pytest.mark.e2e
def test_uc14_create_user_duplicate_email_shows_error(driver):
    """UC-14: creare un utente con un'email gia' registrata mostra un errore."""
    _open_admin(driver)
    suffix = _unique_suffix()

    driver.find_element(By.ID, "admin-new-user-username").send_keys(f"dup_{suffix}")
    driver.find_element(By.ID, "admin-new-user-first-name").send_keys("Dup")
    driver.find_element(By.ID, "admin-new-user-last-name").send_keys("User")
    # Email gia' presente nel seed.
    driver.find_element(By.ID, "admin-new-user-email").send_keys("citizen@example.com")
    driver.find_element(By.ID, "admin-new-user-password").send_keys("Test1234!")
    Select(driver.find_element(By.ID, "admin-new-user-role")).select_by_value("citizen")
    driver.find_element(By.ID, "admin-new-user-submit").click()

    error = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-error"))
    )
    assert error.is_displayed(), (
        "La creazione di un utente con email duplicata deve mostrare un errore"
    )


# ─────────────────────────────────────────────────────────────────────────────
# UC-14 – Bug noto: la categoria appena creata non compare sempre in tabella
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.implementation_bug(
    "Newly created category is not reliably saved/displayed in the categories "
    "table: it sometimes appears immediately, sometimes only after a page "
    "refresh, and sometimes only after an admin logout+login."
)
def test_uc14_created_category_appears_in_table(driver):
    _open_admin(driver)
    name = f"Selenium Visible {_unique_suffix()}"
    _create_category(driver, name)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-success"))
    )

    # Ricarica la pagina per forzare il reload delle categorie
    driver.refresh()
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-categories-table-body"))
    )

    WebDriverWait(driver, WAIT).until(
        lambda d: any(
            field.get_attribute("value") == name
            for field in d.find_elements(By.CSS_SELECTOR, "input[id^='admin-category-name-']")
        )
    )