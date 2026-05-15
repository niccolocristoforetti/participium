import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL, login_as


@pytest.mark.e2e
def test_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")
    assert driver.find_element(By.ID, "login-page").is_displayed()
    assert driver.find_element(By.ID, "login-form").is_displayed()
    assert driver.find_element(By.ID, "login-identifier").is_displayed()
    assert driver.find_element(By.ID, "login-password").is_displayed()
    assert driver.find_element(By.ID, "login-submit").is_displayed()


@pytest.mark.e2e
def test_login_citizen_redirects_to_dashboard(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").clear()
    driver.find_element(By.ID, "login-identifier").send_keys("citizen@example.com")
    driver.find_element(By.ID, "login-password").clear()
    driver.find_element(By.ID, "login-password").send_keys("Citizen123!")
    driver.find_element(By.ID, "login-submit").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
    assert "/dashboard" in driver.current_url


@pytest.mark.e2e
def test_login_operator_redirects_to_operator(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").clear()
    driver.find_element(By.ID, "login-identifier").send_keys("operator@example.com")
    driver.find_element(By.ID, "login-password").clear()
    driver.find_element(By.ID, "login-password").send_keys("Operator123!")
    driver.find_element(By.ID, "login-submit").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/operator"))
    assert "/operator" in driver.current_url


@pytest.mark.e2e
def test_login_admin_redirects_to_admin(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").clear()
    driver.find_element(By.ID, "login-identifier").send_keys("admin@example.com")
    driver.find_element(By.ID, "login-password").clear()
    driver.find_element(By.ID, "login-password").send_keys("Admin123!")
    driver.find_element(By.ID, "login-submit").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/admin"))
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
def test_login_unknown_user_shows_error(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "login-identifier").clear()
    driver.find_element(By.ID, "login-identifier").send_keys("nonexistent@example.com")
    driver.find_element(By.ID, "login-password").clear()
    driver.find_element(By.ID, "login-password").send_keys("Whatever123!")
    driver.find_element(By.ID, "login-submit").click()
    error = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-error"))
    )
    assert error.is_displayed()


@pytest.mark.e2e
def test_login_already_authenticated_redirects(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/login")
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
    assert "/login" not in driver.current_url


@pytest.mark.e2e
def test_login_demo_accounts_visible(driver):
    driver.get(f"{BASE_URL}/login")
    assert driver.find_element(By.ID, "login-demo-accounts").is_displayed()
    assert driver.find_element(By.ID, "login-demo-citizen-email").text == "citizen@example.com"
    assert driver.find_element(By.ID, "login-demo-operator-email").text == "operator@example.com"
    assert driver.find_element(By.ID, "login-demo-admin-email").text == "admin@example.com"
