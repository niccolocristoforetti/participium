import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: end-to-end UI tests executed with Selenium")
    config.addinivalue_line("markers", "implementation_bug: documents an implementation bug revealed by a failing test")

BASE_URL = "http://localhost:5173"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # decommentare per CI
    d = webdriver.Chrome(options=options)
    d.implicitly_wait(5)
    yield d
    d.quit()


def login_as(driver, email, password):
    driver.get(f"{BASE_URL}/login")
    identifier_input = driver.find_element(By.ID, "login-identifier")
    identifier_input.clear()
    identifier_input.send_keys(email)
    password_input = driver.find_element(By.ID, "login-password")
    password_input.clear()
    password_input.send_keys(password)
    driver.find_element(By.ID, "login-submit").click()
    WebDriverWait(driver, 10).until(lambda d: "/login" not in d.current_url)
