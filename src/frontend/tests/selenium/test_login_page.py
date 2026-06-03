"""
Test di accettazione Selenium per:
  UC-02 – Login

UC-02 copre:
  - Il login di un cittadino reindirizza alla dashboard.
  - Il login di un operatore reindirizza all'area operatore.
  - Il login di un amministratore reindirizza al pannello admin.
  - Extension 4a: credenziali errate mostrano un messaggio di errore e mantengono l'utente sulla pagina di login.
  - Un utente gia' autenticato che apre /login viene reindirizzato fuori.
  - Extension 4b: un account registrato ma non verificato non puo' autenticarsi e mostra un errore.
  - Gli account demo (cittadino, operatore, admin) sono visibili nella pagina di login.
"""

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL, login_as


# UC-02: Verifica che il login di un cittadino reindirizzi alla dashboard
@pytest.mark.e2e
def test_login_citizen_redirects_to_dashboard(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    assert "/dashboard" in driver.current_url


# UC-02: Verifica che il login di un operatore reindirizzi all'area operatore
@pytest.mark.e2e
def test_login_operator_redirects_to_operator(driver):
    login_as(driver, "operator@example.com", "Operator123!")
    assert "/operator" in driver.current_url


# UC-02: Verifica che il login di un amministratore reindirizzi al pannello admin
@pytest.mark.e2e
def test_login_admin_redirects_to_admin(driver):
    login_as(driver, "admin@example.com", "Admin123!")
    assert "/admin" in driver.current_url


# UC-02, Extension 4a: Verifica che credenziali errate mostrino un errore e trattengano l'utente su /login
@pytest.mark.e2e
def test_login_wrong_password_shows_error(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").clear()
    driver.find_element(By.ID, "login-identifier").send_keys("citizen@example.com")
    driver.find_element(By.ID, "login-password").clear()
    driver.find_element(By.ID, "login-password").send_keys("WrongPassword!")
    driver.find_element(By.ID, "login-submit").click()
    error = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-error"))
    )
    assert error.is_displayed()
    assert "/login" in driver.current_url


# UC-02: Verifica che un utente gia' autenticato che apre /login venga reindirizzato fuori
@pytest.mark.e2e
def test_login_already_authenticated_redirects(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/login")
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
    assert "/login" not in driver.current_url


# UC-02, Extension 4b: Verifica che un account non verificato non possa autenticarsi e mostri un errore
@pytest.mark.e2e
def test_login_unverified_account_shows_error(driver):
    ts = int(time.time() * 1000)
    username = f"unverified_{ts}"
    email = f"unverified_{ts}@example.com"
    password = "Test1234!"

    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "register-username").send_keys(username)
    driver.find_element(By.ID, "register-first-name").send_keys("Test")
    driver.find_element(By.ID, "register-last-name").send_keys("User")
    driver.find_element(By.ID, "register-email").send_keys(email)
    driver.find_element(By.ID, "register-password").send_keys(password)
    driver.find_element(By.ID, "register-submit").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "register-success"))
    )

    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").send_keys(email)
    driver.find_element(By.ID, "login-password").send_keys(password)
    driver.find_element(By.ID, "login-submit").click()
    error = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-error"))
    )
    assert error.is_displayed()
    assert "/login" in driver.current_url


# UC-02: Verifica che gli account demo siano visibili con le email corrette nella pagina di login
@pytest.mark.e2e
def test_login_demo_accounts_visible(driver):
    driver.get(f"{BASE_URL}/login")
    assert driver.find_element(By.ID, "login-demo-accounts").is_displayed()
    assert driver.find_element(By.ID, "login-demo-citizen-email").text == "citizen@example.com"
    assert driver.find_element(By.ID, "login-demo-operator-email").text == "operator@example.com"
    assert driver.find_element(By.ID, "login-demo-admin-email").text == "admin@example.com"