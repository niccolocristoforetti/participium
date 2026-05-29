import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL, login_as



@pytest.mark.e2e
def test_login_citizen_redirects_to_dashboard(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    assert "/dashboard" in driver.current_url


@pytest.mark.e2e
def test_login_operator_redirects_to_operator(driver):
    login_as(driver, "operator@example.com", "Operator123!")
    assert "/operator" in driver.current_url


@pytest.mark.e2e
def test_login_admin_redirects_to_admin(driver):
    login_as(driver, "admin@example.com", "Admin123!")
    assert "/admin" in driver.current_url


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



@pytest.mark.e2e
def test_login_already_authenticated_redirects(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/login")
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
    assert "/login" not in driver.current_url


@pytest.mark.e2e
def test_login_unverified_account_shows_error(driver):
    # UC-02 Extension 4b: account registrato ma non ancora verificato via email
    ts = int(time.time() * 1000)
    username = f"unverified_{ts}"
    email = f"unverified_{ts}@example.com"
    password = "Test1234!"

    # Registra un nuovo utente (rimane non verificato)
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

    # Tenta il login senza aver verificato l'email
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").send_keys(email)
    driver.find_element(By.ID, "login-password").send_keys(password)
    driver.find_element(By.ID, "login-submit").click()
    error = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-error"))
    )
    assert error.is_displayed()
    assert "/login" in driver.current_url


@pytest.mark.e2e
def test_login_demo_accounts_visible(driver):
    driver.get(f"{BASE_URL}/login")
    assert driver.find_element(By.ID, "login-demo-accounts").is_displayed()
    assert driver.find_element(By.ID, "login-demo-citizen-email").text == "citizen@example.com"
    assert driver.find_element(By.ID, "login-demo-operator-email").text == "operator@example.com"
    assert driver.find_element(By.ID, "login-demo-admin-email").text == "admin@example.com"
