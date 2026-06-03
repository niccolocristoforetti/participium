"""
Test di accettazione Selenium per:
  UC-01 – Registra account

UC-01 copre:
  - La pagina di registrazione si carica con tutti i campi del form.
  - Una registrazione valida mostra la conferma e il link di verifica con l'email inserita.
  - Extension 4b: un'email gia' registrata mostra un errore.
  - Extension 4a: uno username gia' esistente mostra un errore.
  - Extension 4c: i campi obbligatori mancanti bloccano l'invio del form.
  - Extension 5a: un link di verifica non valido mantiene l'account inattivo e il login successivo resta bloccato.
"""

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL


# UC-01: Helper che genera dati utente univoci per ogni esecuzione
def _unique_user():
    ts = int(time.time() * 1000)
    return {
        "username": f"testuser_{ts}",
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser_{ts}@example.com",
        "password": "Test1234!",
    }


# UC-01: Helper che compila e invia il form di registrazione con i dati forniti
def _submit_register_form(driver, user: dict) -> None:
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "register-username").send_keys(user["username"])
    driver.find_element(By.ID, "register-first-name").send_keys(user["first_name"])
    driver.find_element(By.ID, "register-last-name").send_keys(user["last_name"])
    driver.find_element(By.ID, "register-email").send_keys(user["email"])
    driver.find_element(By.ID, "register-password").send_keys(user["password"])
    driver.find_element(By.ID, "register-submit").click()


# UC-01: Verifica che la pagina di registrazione mostri tutti i campi del form
@pytest.mark.e2e
def test_register_page_loads(driver):
    driver.get(f"{BASE_URL}/register")
    assert driver.find_element(By.ID, "register-page").is_displayed()
    assert driver.find_element(By.ID, "register-form").is_displayed()
    assert driver.find_element(By.ID, "register-username").is_displayed()
    assert driver.find_element(By.ID, "register-first-name").is_displayed()
    assert driver.find_element(By.ID, "register-last-name").is_displayed()
    assert driver.find_element(By.ID, "register-email").is_displayed()
    assert driver.find_element(By.ID, "register-password").is_displayed()
    assert driver.find_element(By.ID, "register-submit").is_displayed()


# UC-01: Verifica che una registrazione valida mostri la conferma e il link di verifica
@pytest.mark.e2e
def test_register_success_shows_confirmation_and_verification_link(driver):
    user = _unique_user()
    _submit_register_form(driver, user)
    success = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "register-success"))
    )
    assert success.is_displayed()
    assert user["email"] in success.text
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "verification-box"))
    )
    link = driver.find_element(By.ID, "verification-link")
    assert link.is_displayed()
    assert "verify" in link.get_attribute("href")


# UC-01, Extension 4b: Verifica che un'email gia' registrata mostri un errore
@pytest.mark.e2e
def test_register_duplicate_email_shows_error(driver):
    _submit_register_form(driver, {
        "username": f"unique_{int(time.time() * 1000)}",
        "first_name": "Test", "last_name": "User",
        "email": "citizen@example.com",
        "password": "Test1234!",
    })
    error = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "register-error"))
    )
    assert error.is_displayed()


# UC-01, Extension 4a: Verifica che uno username gia' esistente mostri un errore
@pytest.mark.e2e
def test_register_duplicate_username_shows_error(driver):
    _submit_register_form(driver, {
        "username": "citizen",
        "first_name": "Test", "last_name": "User",
        "email": f"unique_{int(time.time() * 1000)}@example.com",
        "password": "Test1234!",
    })
    error = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "register-error"))
    )
    assert error.is_displayed()


# UC-01, Extension 4c: Verifica che i campi obbligatori mancanti blocchino l'invio del form
@pytest.mark.e2e
def test_register_missing_required_fields_blocked(driver):
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "register-submit").click()
    assert "/register" in driver.current_url
    assert not driver.find_elements(By.ID, "register-success")


# UC-01, Extension 5a: Verifica che un link di verifica non valido mantenga l'account inattivo e blocchi il login
@pytest.mark.e2e
def test_register_invalid_verification_link_keeps_account_inactive(driver):
    user = _unique_user()
    _submit_register_form(driver, user)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "register-success"))
    )

    try:
        real_link = driver.find_element(By.ID, "verification-link").get_attribute("href") or ""
        if "/verify/" in real_link:
            base_path = real_link[: real_link.index("/verify/") + len("/verify/")]
            invalid_url = f"{base_path}invalid-expired-token-000"
        else:
            invalid_url = f"{BASE_URL}/verify/invalid-expired-token-000"
    except Exception:
        invalid_url = f"{BASE_URL}/verify/invalid-expired-token-000"

    driver.get(invalid_url)

    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").send_keys(user["email"])
    driver.find_element(By.ID, "login-password").send_keys(user["password"])
    driver.find_element(By.ID, "login-submit").click()

    error = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-error"))
    )
    assert error.is_displayed(), (
        "Con un link di verifica non valido l'account resta inattivo: "
        "il login deve fallire con un messaggio di errore"
    )
    assert "/login" in driver.current_url, (
        "Un account non verificato non deve poter autenticarsi"
    )