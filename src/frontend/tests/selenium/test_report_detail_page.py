"""
Test di accettazione Selenium per:
  UC-06 – Visualizza dettaglio segnalazione
  UC-07 – Segui segnalazione

Entrambi i casi d'uso si svolgono sulla pagina di dettaglio (/reports/<id>).

UC-06 copre:
  - La pagina è accessibile senza autenticazione.
  - Titolo, stato, descrizione, categoria, reporter, date e contatore follower sono visibili.
  - La sezione mappa è presente.
  - La sezione foto è presente.
  - La cronologia degli stati è presente.
  - La sezione messaggi è presente.
  - Extension 2a: un ID inesistente mostra il messaggio di non disponibilità.

UC-07 copre:
  - Extension 3b: il pulsante Follow non è visibile per i visitatori non autenticati.
  - Cliccando Follow il bottone diventa 'Unfollow report'.
  - Cliccando Unfollow il bottone torna a 'Follow report'.
  - Nota: il test è marcato implementation_bug per via di una race condition React 19
    StrictMode che impedisce a Selenium di osservare il cambio di stato immediato.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL, login_as


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_seed_report_url(driver) -> str:
    """Ritorna l'URL del primo report pubblico disponibile nella tabella della home."""
    driver.get(BASE_URL)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "home-page"))
    )
    links = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "tr[id^='public-report-row-'] [id$='-open-link']")
        )
    )
    return links[0].get_attribute("href")


def _wait_detail_loaded(driver, timeout: int = 10) -> None:
    """Aspetta che la pagina di dettaglio sia completamente caricata."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "report-detail-page"))
    )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "report-detail-title"))
    )


_LINK_CSS = "tr[id^='public-report-row-'] [id$='-open-link']"


def _go_to_first_public_report(driver) -> None:
    """Naviga al primo report pubblico via nav-home e link tabella (client-side nav)."""
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "nav-home"))
    )
    driver.find_element(By.ID, "nav-home").click()
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "home-page"))
    )
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, _LINK_CSS))
    ).click()
    _wait_detail_loaded(driver)


# ─────────────────────────────────────────────────────────────────────────────
# UC-06 – Visualizza dettaglio segnalazione
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc06_detail_page_accessible_without_login(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)
    assert driver.find_element(By.ID, "report-detail-page").is_displayed()


@pytest.mark.e2e
def test_uc06_detail_shows_required_fields(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    for element_id in (
        "report-detail-title",
        "report-detail-status",
        "report-detail-description",
        "report-detail-category-value",
        "report-detail-reporter-value",
        "report-detail-followers-value",
        "report-detail-created-value",
        "report-detail-updated-value",
    ):
        assert driver.find_element(By.ID, element_id).is_displayed(), (
            f"Il campo '{element_id}' deve essere visibile nella pagina di dettaglio"
        )


@pytest.mark.e2e
def test_uc06_detail_shows_map_section(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "report-detail-map-card").is_displayed()
    assert driver.find_element(By.ID, "report-detail-map-title").is_displayed()
    assert driver.find_element(By.ID, "report-detail-map").is_displayed()


@pytest.mark.e2e
def test_uc06_detail_shows_photos_section(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "report-detail-photos-card").is_displayed()
    assert driver.find_element(By.ID, "report-detail-photos-title").is_displayed()
    assert driver.find_element(By.ID, "report-detail-photo-grid").is_displayed()


@pytest.mark.e2e
def test_uc06_detail_shows_status_history(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "status-history-card").is_displayed()
    assert driver.find_element(By.ID, "status-history-title").is_displayed()
    assert driver.find_element(By.ID, "status-history-list").is_displayed()


@pytest.mark.e2e
def test_uc06_detail_shows_messages_section(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "messages-card").is_displayed()


@pytest.mark.e2e
def test_uc06_detail_unavailable_for_invalid_id(driver):
    driver.get(f"{BASE_URL}/reports/999999999")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "report-detail-page"))
    )
    assert driver.find_element(By.ID, "report-detail-error").is_displayed()
    assert not driver.find_elements(By.ID, "report-detail-title"), (
        "Con un ID inesistente non deve essere mostrato il contenuto del report"
    )


# ─────────────────────────────────────────────────────────────────────────────
# UC-07 – Segui segnalazione
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_uc07_follow_button_hidden_for_visitor(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert not driver.find_elements(By.ID, "follow-button"), (
        "Il pulsante Follow non deve essere visibile per un visitatore non autenticato"
    )


@pytest.mark.e2e
@pytest.mark.implementation_bug(
    "The follow button requires a double click to work: React 19 StrictMode fires "
    "loadReport() twice on mount; the second call resolves after handleFollowToggle "
    "and overwrites the updated state before Selenium can observe the change."
)
@pytest.mark.xfail(reason="React 19 StrictMode double-mount overwrites follow state", strict=False)
def test_uc07_follow_report(driver):
    """UC-07: Segui e togli il follow a un report come cittadino autenticato."""
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/reports/3")
    _wait_detail_loaded(driver)

    wait = WebDriverWait(driver, 10)
    follow_btn = wait.until(EC.element_to_be_clickable((By.ID, "follow-button")))

    # Reset: se già seguito, prima togli il follow
    if follow_btn.text.strip() == "Unfollow report":
        follow_btn.click()
        wait.until(lambda d: d.find_element(By.ID, "follow-button").text == "Follow report")
        follow_btn = driver.find_element(By.ID, "follow-button")

    follow_btn.click()
    wait.until(lambda d: d.find_element(By.ID, "follow-button").text == "Unfollow report")
    driver.find_element(By.ID, "follow-button").click()
    wait.until(lambda d: d.find_element(By.ID, "follow-button").text == "Follow report")