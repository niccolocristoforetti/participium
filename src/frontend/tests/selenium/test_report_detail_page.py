"""
Test di accettazione Selenium per:
  UC-06 – Visualizza dettaglio segnalazione
  UC-07 – Segui segnalazione

Entrambi i casi d'uso si svolgono sulla pagina di dettaglio (/reports/<id>).

UC-06 copre:
  - La pagina di dettaglio e' accessibile senza autenticazione.
  - Titolo, stato, descrizione, categoria, reporter, date e contatore follower sono visibili.
  - La sezione mappa e' presente.
  - La sezione foto e' presente.
  - La cronologia degli stati e' presente.
  - La sezione messaggi e' presente.
  - Extension 2a: un ID inesistente mostra il messaggio di non disponibilita'.

UC-07 copre:
  - Extension 3b: il pulsante Follow non e' visibile per i visitatori non autenticati.
  - Cliccando Follow il bottone diventa 'Unfollow report' e viceversa
    (test marcato implementation_bug per una race condition React 19 StrictMode).
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL, login_as


# UC-06: Helper che ritorna l'URL del primo report pubblico disponibile nella home
def _get_seed_report_url(driver) -> str:
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


# UC-06: Helper che attende il caricamento completo della pagina di dettaglio
def _wait_detail_loaded(driver, timeout: int = 10) -> None:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "report-detail-page"))
    )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "report-detail-title"))
    )


_LINK_CSS = "tr[id^='public-report-row-'] [id$='-open-link']"


# UC-06: Helper che naviga al primo report pubblico via nav-home e link tabella
def _go_to_first_public_report(driver) -> None:
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


# UC-06: Verifica che la pagina di dettaglio sia accessibile senza login
@pytest.mark.e2e
def test_uc06_detail_page_accessible_without_login(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)
    assert driver.find_element(By.ID, "report-detail-page").is_displayed()


# UC-06: Verifica che il dettaglio mostri titolo, stato, descrizione, categoria, reporter, follower e date
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


# UC-06: Verifica che la sezione mappa del dettaglio sia visibile
@pytest.mark.e2e
def test_uc06_detail_shows_map_section(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "report-detail-map-card").is_displayed()
    assert driver.find_element(By.ID, "report-detail-map-title").is_displayed()
    assert driver.find_element(By.ID, "report-detail-map").is_displayed()


# UC-06: Verifica che la sezione foto del dettaglio sia visibile
@pytest.mark.e2e
def test_uc06_detail_shows_photos_section(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "report-detail-photos-card").is_displayed()
    assert driver.find_element(By.ID, "report-detail-photos-title").is_displayed()
    assert driver.find_element(By.ID, "report-detail-photo-grid").is_displayed()


# UC-06: Verifica che la cronologia degli stati sia visibile
@pytest.mark.e2e
def test_uc06_detail_shows_status_history(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "status-history-card").is_displayed()
    assert driver.find_element(By.ID, "status-history-title").is_displayed()
    assert driver.find_element(By.ID, "status-history-list").is_displayed()


# UC-06: Verifica che la sezione messaggi sia visibile
@pytest.mark.e2e
def test_uc06_detail_shows_messages_section(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert driver.find_element(By.ID, "messages-card").is_displayed()


# UC-06, Extension 2a: Verifica che un ID inesistente mostri l'errore e nasconda il contenuto del report
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

# UC-07, Extension 3a: Verifica che per un report gia' seguito il pulsante mostri 'Unfollow report',
# offrendo quindi l'azione di Unfollow al cittadino che e' gia' follower
@pytest.mark.e2e
@pytest.mark.xfail(
    reason="React 19 StrictMode double-mount: loadReport() risolve due volte e puo' "
           "sovrascrivere lo stato is_followed_by_current_user prima dell'asserzione",
    strict=False,
)
def test_uc07_already_following_offers_unfollow(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/reports/3")
    _wait_detail_loaded(driver)

    wait = WebDriverWait(driver, 10)
    follow_btn = wait.until(EC.element_to_be_clickable((By.ID, "follow-button")))

    # Porta il report nello stato 'seguito' se non lo e' gia'
    if follow_btn.text.strip() == "Follow report":
        follow_btn.click()
        wait.until(lambda d: d.find_element(By.ID, "follow-button").text.strip() == "Unfollow report")

    # Extension 3a: essendo gia' follower, il sistema deve esporre l'azione di Unfollow
    assert driver.find_element(By.ID, "follow-button").text.strip() == "Unfollow report", (
        "Per un report gia' seguito il pulsante deve offrire 'Unfollow report'"
    )

# UC-07, Extension 3b: Verifica che il pulsante Follow sia nascosto ai visitatori non autenticati
@pytest.mark.e2e
def test_uc07_follow_button_hidden_for_visitor(driver):
    url = _get_seed_report_url(driver)
    driver.get(url)
    _wait_detail_loaded(driver)

    assert not driver.find_elements(By.ID, "follow-button"), (
        "Il pulsante Follow non deve essere visibile per un visitatore non autenticato"
    )


# UC-07: Verifica che un cittadino autenticato possa seguire e poi smettere di seguire un report
@pytest.mark.e2e
@pytest.mark.implementation_bug(
   "Il pulsante 'Segui' richiede un doppio clic per funzionare: React 19 StrictMode attiva "
    "loadReport() due volte al montaggio; la seconda chiamata viene risolta dopo handleFollowToggle "
    "e sovrascrive lo stato aggiornato prima che Selenium possa rilevare la modifica."
)
@pytest.mark.xfail(reason="React 19 StrictMode attiva", strict=False)
def test_uc07_follow_report(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/reports/3")
    _wait_detail_loaded(driver)

    wait = WebDriverWait(driver, 10)
    follow_btn = wait.until(EC.element_to_be_clickable((By.ID, "follow-button")))

    if follow_btn.text.strip() == "Unfollow report":
        follow_btn.click()
        wait.until(lambda d: d.find_element(By.ID, "follow-button").text == "Follow report")
        follow_btn = driver.find_element(By.ID, "follow-button")

    follow_btn.click()
    wait.until(lambda d: d.find_element(By.ID, "follow-button").text == "Unfollow report")
    driver.find_element(By.ID, "follow-button").click()
    wait.until(lambda d: d.find_element(By.ID, "follow-button").text == "Follow report")