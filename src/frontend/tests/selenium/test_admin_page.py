"""
Test di accettazione Selenium per:
  UC-13 – Visualizza statistiche private
  UC-14 – Gestisci categorie e configurazione (categorie e account utente)

Entrambi i casi d'uso si svolgono nel pannello di amministrazione (/admin),
una rotta protetta riservata al ruolo Administrator: il controllo accessi viene
esercitato prima dei flussi funzionali.

UC-13 copre:
  - La sezione statistiche e' visibile.
  - Sono presenti le viste per stato, tipo/categoria, reporter e top reporter.

UC-14 copre:
  - Solo l'amministratore puo' accedere alla configurazione (rotta protetta e vietata ai cittadini).
  - I form di creazione e le tabelle di utenti e categorie sono visibili.
  - Una nuova categoria puo' essere creata (messaggio di conferma).
  - Extension 4b: un nome di categoria duplicato mostra un errore.
  - Una categoria esistente del seed puo' essere aggiornata.
  - Un nuovo utente / operatore con categoria puo' essere creato.
  - Un utente esistente del seed puo' essere aggiornato.
  - Un'email gia' registrata blocca la creazione di un nuovo utente.
  - Bug noto: la categoria appena creata non compare in modo affidabile in tabella senza refresh / re-login.
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

WAIT = 15


# UC-14: Helper che genera un suffisso univoco basato sul timestamp
def _unique_suffix() -> str:
    return str(int(time.time() * 1000))


# UC-14: Helper che svuota un campo in modo robusto e vi scrive il valore indicato
def _type(driver, element, value: str) -> None:
    element.click()
    element.send_keys(Keys.CONTROL, "a")
    element.send_keys(Keys.DELETE)
    element.clear()
    element.send_keys(value)


# UC-14: Helper di login resiliente che riprova se si resta sulla pagina di login
def _login(driver, email: str, password: str, attempts: int = 3) -> None:
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


# UC-13: Helper che effettua il login come amministratore e attende il pannello admin con dati caricati
def _open_admin(driver) -> None:
    _login(driver, ADMIN_EMAIL, ADMIN_PASSWORD)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-page"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "logout-button"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-users-table-body"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-categories-table-body"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-statistics-section"))
    )
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[id^='admin-user-email-']")
        )
    )


# UC-14: Helper che aggiorna un checkbox React-controlled in modo affidabile in headless Chrome
def _react_set_checkbox(driver, checkbox_element, checked: bool) -> None:
    driver.execute_script(
        "Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'checked')"
        ".set.call(arguments[0], arguments[1]);"
        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        checkbox_element,
        checked,
    )


# UC-14: Helper che compila e invia il form di creazione categoria
def _create_category(driver, name: str) -> None:
    field = driver.find_element(By.ID, "admin-new-category-name")
    _type(driver, field, name)
    driver.find_element(By.ID, "admin-new-category-submit").click()


# UC-14: Helper che attende il messaggio di successo admin, fallendo subito se compare prima un errore
def _wait_admin_success(driver):
    def _outcome(d):
        errors = d.find_elements(By.ID, "admin-error")
        if errors and errors[0].text.strip():
            return ("error", errors[0].text.strip())
        successes = d.find_elements(By.ID, "admin-success")
        if successes and successes[0].text.strip():
            return ("success", successes[0].text.strip())
        return False

    try:
        kind, payload = WebDriverWait(driver, WAIT).until(_outcome)
    except TimeoutException:
        raise AssertionError(
            "Nessun messaggio di successo dopo il salvataggio. admin-error: "
            "nessun messaggio mostrato"
        )
    if kind == "error":
        raise AssertionError(
            f"Nessun messaggio di successo dopo il salvataggio. admin-error: {payload}"
        )
    return payload


# UC-14: Helper che ritorna l'ID UI dell'utente con l'email indicata
def _find_user_id_by_email(driver, email: str) -> str:
    inputs = WebDriverWait(driver, WAIT).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "input[id^='admin-user-email-']")
        )
    )
    for field in inputs:
        if field.get_attribute("value") == email:
            return field.get_attribute("id").replace("admin-user-email-", "")
    raise AssertionError(f"Nessuna riga utente trovata per l'email '{email}'")


# UC-14: Helper che ritorna l'ID UI della categoria con il nome indicato
def _find_category_id_by_name(driver, name: str) -> str:
    inputs = WebDriverWait(driver, WAIT).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "input[id^='admin-category-name-']")
        )
    )
    for field in inputs:
        if field.get_attribute("value") == name:
            return field.get_attribute("id").replace("admin-category-name-", "")
    raise AssertionError(f"Nessuna riga categoria trovata per il nome '{name}'")


# UC-14: Helper best-effort che riporta il flag attivo di una categoria al valore desiderato
def _restore_category_active(driver, category_id: str, target_active: bool) -> None:
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


# UC-14: Helper best-effort che riporta la preferenza notifiche email di un utente al valore desiderato
def _restore_user_email_notifications(driver, user_id: str, target_state: bool) -> None:
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


# UC-14: Verifica che un visitatore non autenticato venga reindirizzato al login
@pytest.mark.e2e
def test_admin_requires_authentication(driver):
    driver.get(f"{BASE_URL}/admin")
    WebDriverWait(driver, WAIT).until(lambda d: "/login" in d.current_url)
    assert "/login" in driver.current_url


# UC-14: Verifica che un cittadino autenticato non possa accedere al pannello admin
@pytest.mark.e2e
def test_admin_forbidden_for_citizen(driver):
    _login(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/admin")
    WebDriverWait(driver, WAIT).until(lambda d: "/admin" not in d.current_url)
    assert "/admin" not in driver.current_url, (
        "Un ruolo non admin deve essere reindirizzato fuori dal pannello admin"
    )
    assert not driver.find_elements(By.ID, "admin-page")


# UC-14: Verifica che il pannello admin mostri i form di creazione e le tabelle
@pytest.mark.e2e
def test_admin_page_loads_for_admin(driver):
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


# UC-13: Verifica che siano visibili le statistiche per stato, tipo, reporter e top reporter
@pytest.mark.e2e
def test_uc13_statistics_sections_visible(driver):
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


# UC-14: Verifica che la creazione di una nuova categoria confermi con un messaggio di successo
@pytest.mark.e2e
def test_uc14_create_category_shows_success(driver):
    _open_admin(driver)
    name = f"Selenium Category {_unique_suffix()}"
    _create_category(driver, name)

    success = _wait_admin_success(driver)
    assert "Category created." in success, (
        "La creazione della categoria deve mostrare il messaggio di conferma"
    )


# UC-14, Extension 4b: Verifica che un nome di categoria gia' esistente mostri un errore
@pytest.mark.e2e
def test_uc14_create_duplicate_category_shows_error(driver):
    _open_admin(driver)
    _create_category(driver, "Waste")
    error = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-error"))
    )
    assert error.is_displayed(), (
        "La creazione di una categoria con nome duplicato deve mostrare un errore"
    )


# UC-14: Verifica che una categoria esistente del seed possa essere aggiornata e salvata
@pytest.mark.e2e
def test_uc14_update_existing_category_succeeds(driver):
    _open_admin(driver)
    category_id = _find_category_id_by_name(driver, "Other")

    try:
        active_id = f"admin-category-active-{category_id}"
        save_id = f"admin-category-save-{category_id}"
        active = driver.find_element(By.ID, active_id)
        target = not active.is_selected()
        _react_set_checkbox(driver, driver.find_element(By.ID, active_id), target)
        WebDriverWait(driver, WAIT).until(
            lambda d: d.find_element(By.ID, active_id).is_selected() == target
        )
        driver.execute_script(
            "arguments[0].click();",
            driver.find_element(By.ID, save_id),
        )

        def _category_outcome(d):
            errors = d.find_elements(By.ID, "admin-error")
            if errors and errors[0].text.strip():
                return ("error", errors[0].text.strip())
            successes = d.find_elements(By.ID, "admin-success")
            if successes and successes[0].text.strip():
                return ("success", successes[0].text.strip())
            return False

        kind, payload = WebDriverWait(driver, WAIT).until(_category_outcome)
        assert kind == "success", f"Salvataggio categoria fallito: admin-error: {payload}"
        success_text = payload
        assert f"Category #{category_id} updated." in success_text, (
            f"Messaggio di successo inatteso: '{success_text}'"
        )
    finally:
        _restore_category_active(driver, category_id, target_active=True)


# UC-14: Verifica che la creazione di un nuovo account cittadino confermi con un messaggio
@pytest.mark.e2e
def test_uc14_create_user_shows_success(driver):
    _open_admin(driver)
    suffix = _unique_suffix()
    email = f"selenium_user_{suffix}@example.com"

    driver.find_element(By.ID, "admin-new-user-username").send_keys(f"sel_user_{suffix}")
    driver.find_element(By.ID, "admin-new-user-first-name").send_keys("Selenium")
    driver.find_element(By.ID, "admin-new-user-last-name").send_keys("User")
    driver.find_element(By.ID, "admin-new-user-email").send_keys(email)
    driver.find_element(By.ID, "admin-new-user-password").send_keys("Test1234!")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#admin-new-user-role option[value]"))
    )
    Select(driver.find_element(By.ID, "admin-new-user-role")).select_by_value("citizen")
    WebDriverWait(driver, WAIT).until(
        lambda d: d.find_element(By.ID, "admin-new-user-role").get_attribute("value") == "citizen"
    )
    driver.find_element(By.ID, "admin-new-user-submit").click()

    success = _wait_admin_success(driver)
    assert "User created." in success, (
        "La creazione dell'utente deve mostrare il messaggio di conferma"
    )


# UC-14: Verifica che la creazione di un operatore con categoria assegnata confermi con un messaggio
@pytest.mark.e2e
def test_uc14_create_operator_with_category_shows_success(driver):
    _open_admin(driver)
    suffix = _unique_suffix()
    email = f"selenium_op_{suffix}@example.com"

    driver.find_element(By.ID, "admin-new-user-username").send_keys(f"sel_op_{suffix}")
    driver.find_element(By.ID, "admin-new-user-first-name").send_keys("Selenium")
    driver.find_element(By.ID, "admin-new-user-last-name").send_keys("Operator")
    driver.find_element(By.ID, "admin-new-user-email").send_keys(email)
    driver.find_element(By.ID, "admin-new-user-password").send_keys("Test1234!")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#admin-new-user-role option[value='operator']")
        )
    )
    Select(driver.find_element(By.ID, "admin-new-user-role")).select_by_value("operator")
    WebDriverWait(driver, WAIT).until(
        lambda d: d.find_element(By.ID, "admin-new-user-role").get_attribute("value") == "operator"
    )

    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#admin-new-user-category option[value]:not([value=''])")
        )
    )
    category_select = Select(driver.find_element(By.ID, "admin-new-user-category"))
    real_options = [
        opt for opt in category_select.options if (opt.get_attribute("value") or "").strip()
    ]
    assert real_options, "Devono esistere categorie attive da assegnare all'operatore"
    category_select.select_by_value(real_options[0].get_attribute("value"))

    driver.find_element(By.ID, "admin-new-user-submit").click()
    success = _wait_admin_success(driver)
    assert "User created." in success, (
        "La creazione dell'operatore deve mostrare il messaggio di conferma"
    )


# UC-14: Verifica che un account utente esistente del seed possa essere modificato e salvato
@pytest.mark.e2e
def test_uc14_update_existing_user_succeeds(driver):
    _open_admin(driver)
    user_id = _find_user_id_by_email(driver, "operator@example.com")

    flag_id = f"admin-user-email-notifications-{user_id}"
    save_id = f"admin-user-save-{user_id}"
    original_state = driver.find_element(By.ID, flag_id).is_selected()

    try:
        target = not original_state
        _react_set_checkbox(driver, driver.find_element(By.ID, flag_id), target)
        WebDriverWait(driver, WAIT).until(
            lambda d: d.find_element(By.ID, flag_id).is_selected() == target
        )
        driver.execute_script(
            "arguments[0].click();",
            driver.find_element(By.ID, save_id),
        )

        success = _wait_admin_success(driver)
        assert f"User #{user_id} updated." in success, (
            "L'aggiornamento dell'utente deve mostrare il messaggio di conferma"
        )
    finally:
        _restore_user_email_notifications(driver, user_id, original_state)


# UC-14, Extension 4b: Verifica che creare un utente con un'email gia' registrata mostri un errore
@pytest.mark.e2e
def test_uc14_create_user_duplicate_email_shows_error(driver):
    _open_admin(driver)
    suffix = _unique_suffix()

    driver.find_element(By.ID, "admin-new-user-username").send_keys(f"dup_{suffix}")
    driver.find_element(By.ID, "admin-new-user-first-name").send_keys("Dup")
    driver.find_element(By.ID, "admin-new-user-last-name").send_keys("User")
    driver.find_element(By.ID, "admin-new-user-email").send_keys("citizen@example.com")
    driver.find_element(By.ID, "admin-new-user-password").send_keys("Test1234!")
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#admin-new-user-role option[value='citizen']")
        )
    )
    Select(driver.find_element(By.ID, "admin-new-user-role")).select_by_value("citizen")
    driver.find_element(By.ID, "admin-new-user-submit").click()

    error = WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-error"))
    )
    assert error.is_displayed(), (
        "La creazione di un utente con email duplicata deve mostrare un errore"
    )


# UC-14: Verifica che la categoria appena creata compaia in tabella dopo refresh (bug noto, non affidabile)
@pytest.mark.implementation_bug(
    "La categoria appena creata non viene salvata/visualizzata in modo affidabile nella tabella delle categorie"
    "A volte appare immediatamente, a volte solo dopo un aggiornamento della pagina"
    "e a volte solo dopo un logout e un login da amministratore."
)
def test_uc14_created_category_appears_in_table(driver):
    _open_admin(driver)
    name = f"Selenium Visible {_unique_suffix()}"
    _create_category(driver, name)
    WebDriverWait(driver, WAIT).until(
        EC.presence_of_element_located((By.ID, "admin-success"))
    )

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