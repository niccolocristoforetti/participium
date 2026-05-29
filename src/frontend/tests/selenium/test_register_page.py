import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL


def _unique_user():
    ts = int(time.time() * 1000)
    return {
        "username": f"testuser_{ts}",
        "first_name": "Test",
        "last_name": "User",
        "email": f"testuser_{ts}@example.com",
        "password": "Test1234!",
    }


def _submit_register_form(driver, user: dict) -> None:
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "register-username").send_keys(user["username"])
    driver.find_element(By.ID, "register-first-name").send_keys(user["first_name"])
    driver.find_element(By.ID, "register-last-name").send_keys(user["last_name"])
    driver.find_element(By.ID, "register-email").send_keys(user["email"])
    driver.find_element(By.ID, "register-password").send_keys(user["password"])
    driver.find_element(By.ID, "register-submit").click()


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


@pytest.mark.e2e
def test_register_missing_required_fields_blocked(driver):
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "register-submit").click()
    # Il browser blocca il submit per i campi `required` — la pagina non cambia
    assert "/register" in driver.current_url
    assert not driver.find_elements(By.ID, "register-success")
