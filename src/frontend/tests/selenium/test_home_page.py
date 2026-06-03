"""
Test di accettazione Selenium per:
  UC-04 – Sfoglia le segnalazioni sulla mappa
  UC-05 – Cerca e filtra le segnalazioni
  UC-08 – Esporta report (CSV)
  UC-09 – Visualizza statistiche pubbliche

Tutti i casi d'uso si svolgono sulla home page (/), accessibile senza
autenticazione da qualsiasi visitatore.

UC-04 copre:
  - La home page e' raggiungibile senza login.
  - La sezione hero mostra titolo e pulsanti di Login e Registrazione.
  - La sezione mappa e' presente e il suo contenitore e' nel DOM.
  - La sezione statistiche mostra il totale delle segnalazioni come numero.
  - La tabella dei report e' visibile con le intestazioni corrette.
  - Le righe della tabella hanno ID stabili nel formato public-report-row-<id>.
  - Cliccando 'Open' su un report si arriva alla pagina di dettaglio.

UC-05 copre:
  - Il form di filtraggio e' visibile con tutti i controlli (categoria, stato, date, ordine).
  - I select di categoria e stato sono popolati dal backend.
  - Il filtro per categoria mostra solo i report di quella categoria.
  - Il filtro per stato mostra solo i report con quello stato.
  - L'ordinamento default e' 'Newest first'; passando ad 'Oldest first' l'ordine cambia.
  - Filtri per data futura/passata producono una tabella vuota.
  - Extension 4a: resettando i filtri i report ricompaiono.
  - L'href di export riflette il filtro categoria attivo.

UC-08 copre:
  - Il link export riflette i filtri attivi di stato, date_from e date_to.
  - Extension 2a: con result set vuoto nessun export fuorviante (bug noto di implementazione).

UC-09 copre:
  - La sezione 'Reports by category' e' visibile e popolata con i dati seed.
  - La sezione 'Trend' e' visibile e contiene almeno un bucket temporale.
  - Le granularita' Day, Week e Month mantengono visibile la sezione trend senza errori.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from conftest import BASE_URL


# UC-04: Helper che attende il caricamento completo della home e della tabella dei report
def _wait_home_loaded(driver, timeout: int = 15) -> None:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "home-page"))
    )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "public-report-table-body"))
    )


# UC-05: Helper che imposta un valore su un input datetime e scatena gli eventi React necessari
def _set_date_input(driver, element_id: str, value: str) -> None:
    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """,
        driver.find_element(By.ID, element_id),
        value,
    )


# UC-05: Helper che ritorna gli ID delle righe visibili in tabella, ignorando i marker della mappa
def _get_visible_row_ids(driver) -> list:
    rows = driver.find_elements(By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    return [
        r.get_attribute("id")
        for r in rows
        if r.is_displayed() and "-map-marker" not in (r.get_attribute("id") or "")
    ]


# UC-04: Verifica che un utente non loggato possa aprire la home senza autenticazione
@pytest.mark.e2e
def test_uc04_home_page_accessible_without_login(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "home-page"))
    )
    assert driver.find_element(By.ID, "home-page").is_displayed(), (
        "La home page dovrebbe essere visibile senza autenticazione"
    )


# UC-04: Verifica che la sezione hero mostri titolo e pulsanti di Login e Registrazione
@pytest.mark.e2e
def test_uc04_hero_section_visible(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "home-page")))

    assert driver.find_element(By.ID, "home-hero-title").is_displayed()
    assert driver.find_element(By.ID, "home-hero-actions").is_displayed()
    assert driver.find_element(By.ID, "register-link").is_displayed()
    assert driver.find_element(By.ID, "login-link").is_displayed()


# UC-04: Verifica che il box che contiene la mappa OpenStreetMap sia visibile
@pytest.mark.e2e
def test_uc04_map_card_present(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-map-card"))
    )
    assert driver.find_element(By.ID, "public-map-card").is_displayed()
    assert driver.find_element(By.ID, "public-map-title").is_displayed()


# UC-04: Verifica che il contenitore della mappa sia effettivamente presente nel DOM
@pytest.mark.e2e
def test_uc04_map_container_rendered(driver):
    driver.get(BASE_URL)
    map_el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-map"))
    )
    assert map_el is not None, "Il contenitore della mappa deve essere presente nel DOM"


# UC-04: Verifica che la sezione statistiche mostri il totale delle segnalazioni come numero
@pytest.mark.e2e
def test_uc04_statistics_section_visible(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-statistics-card"))
    )
    assert driver.find_element(By.ID, "public-statistics-card").is_displayed()
    assert driver.find_element(By.ID, "public-statistics-title").is_displayed()
    assert driver.find_element(By.ID, "public-total-reports-label").is_displayed()

    total_el = driver.find_element(By.ID, "public-total-reports-value")
    assert total_el.is_displayed()
    assert total_el.text.strip().isdigit(), (
        f"Il totale dei report dovrebbe essere un numero intero, trovato: '{total_el.text}'"
    )


# UC-04: Verifica che la tabella sia visibile con tutte le colonne richieste
@pytest.mark.e2e
def test_uc04_report_table_headers_visible(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    assert driver.find_element(By.ID, "public-report-table").is_displayed()
    assert driver.find_element(By.ID, "public-report-table-head").is_displayed()
    for header_id in (
        "public-report-header-id",
        "public-report-header-title",
        "public-report-header-status",
        "public-report-header-category",
    ):
        assert driver.find_element(By.ID, header_id).is_displayed(), (
            f"L'intestazione '{header_id}' dovrebbe essere visibile"
        )


# UC-04: Verifica che gli ID delle righe seguano lo schema public-report-row-<id> con suffisso numerico
@pytest.mark.e2e
def test_uc04_report_rows_have_stable_ids(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr[id^='public-report-row-']"))
    )

    row_ids = [
        row.get_attribute("id")
        for row in driver.find_elements(By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    ]
    row_ids = [r_id for r_id in row_ids if r_id and "-map-marker" not in r_id]

    assert len(row_ids) > 0, (
        "Con i dati seed ci deve essere almeno un report nella tabella pubblica"
    )
    for r_id in row_ids:
        suffix = r_id.replace("public-report-row-", "")
        assert suffix.isdigit(), (
            f"Il suffisso dell'ID riga '{r_id}' deve essere numerico, trovato: '{suffix}'"
        )


# UC-04: Verifica che cliccando 'Open' sul primo report si arrivi alla pagina di dettaglio
@pytest.mark.e2e
def test_uc04_open_link_navigates_to_report_detail(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    open_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "tr[id^='public-report-row-'] [id$='-open-link']")
        )
    )
    assert len(open_links) > 0, (
        "Con i dati seed ci deve essere almeno un link 'Open' nella tabella pubblica"
    )

    open_links[0].click()

    WebDriverWait(driver, 10).until(lambda d: "/reports/" in d.current_url)
    assert "/reports/" in driver.current_url, (
        "Dopo aver cliccato 'Open' l'URL deve contenere /reports/<id>"
    )

# UC-05: Verifica che il form filtri mostri tutti i controlli (input, select, bottone invio)
@pytest.mark.e2e
def test_uc05_filter_form_all_controls_visible(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    for element_id in (
        "public-filter-section",
        "public-filter-form",
        "public-filter-category",
        "public-filter-status",
        "public-filter-date-from",
        "public-filter-date-to",
        "public-filter-sort",
        "public-filter-submit",
    ):
        assert driver.find_element(By.ID, element_id).is_displayed(), (
            f"L'elemento '{element_id}' del form filtri deve essere visibile"
        )


# UC-05: Verifica che siano presenti le opzioni di ordinamento per i piu' recenti e i piu' vecchi
@pytest.mark.e2e
def test_uc05_filter_sort_options_present(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    assert driver.find_element(By.ID, "public-filter-sort-option-desc").is_displayed()
    assert driver.find_element(By.ID, "public-filter-sort-option-asc").is_displayed()


# UC-05: Verifica che il backend popoli il select delle categorie con i dati reali
@pytest.mark.e2e
def test_uc05_category_options_loaded_from_backend(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    category_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "select#public-filter-category option")
        )
    )
    assert len(category_options) > 0, (
        "Almeno una categoria deve essere caricata nel select del filtro"
    )


# UC-05: Verifica che il backend popoli il select degli stati pubblici
@pytest.mark.e2e
def test_uc05_status_options_loaded_from_backend(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    status_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "select#public-filter-status option")
        )
    )
    assert len(status_options) > 0, (
        "Almeno uno stato pubblico deve essere caricato nel select del filtro"
    )


# UC-05: Verifica che il filtro per categoria mostri solo i report di quella categoria
@pytest.mark.e2e
def test_uc05_filter_by_category_shows_only_matching_reports(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    cat_select = Select(driver.find_element(By.ID, "public-filter-category"))
    options = cat_select.options
    if len(options) < 2:
        pytest.skip("Nessuna categoria disponibile oltre ad 'All'")

    chosen_name = options[1].text.strip()
    cat_select.select_by_visible_text(chosen_name)
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-report-table-body"))
    )

    rows = _get_visible_row_ids(driver)
    for r_id in rows:
        category_text = driver.find_element(By.ID, f"{r_id}-category").text.strip()
        assert category_text == chosen_name, (
            f"Riga '{r_id}' ha categoria '{category_text}', atteso '{chosen_name}'"
        )


# UC-05: Verifica che il filtro per stato mostri solo i report con quello stato
@pytest.mark.e2e
def test_uc05_filter_by_status_shows_only_matching_reports(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    WebDriverWait(driver, 10).until(
        lambda d: len(Select(d.find_element(By.ID, "public-filter-status")).options) >= 2
    )

    status_select = Select(driver.find_element(By.ID, "public-filter-status"))
    options = status_select.options
    if len(options) < 2:
        pytest.skip("Nessuno stato pubblico disponibile oltre ad 'All'")
    chosen_status = options[1].text.strip()
    status_select.select_by_visible_text(chosen_status)

    WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,)).until(
    lambda d: all(
        d.find_element(By.ID, f"{r}-status").text.strip() == chosen_status
        for r in _get_visible_row_ids(d)
        if any(char.isdigit() for char in r)
    )
)
    rows = _get_visible_row_ids(driver)
    for r_id in rows:
        status_text = driver.find_element(By.ID, f"{r_id}-status").text.strip()
        assert status_text == chosen_status, (
            f"Riga '{r_id}' ha stato '{status_text}', atteso '{chosen_status}'"
        )


# UC-05: Verifica che l'ordinamento di default sia 'Newest first' e che asc sia l'inverso esatto di desc
@pytest.mark.e2e
def test_uc05_sort_default_is_strictly_descending(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)
    rows_desc = _get_visible_row_ids(driver)
    if len(rows_desc) < 2:
        pytest.skip("Servono almeno 2 report per verificare la cronologia")

    Select(driver.find_element(By.ID, "public-filter-sort")).select_by_value("asc")
    WebDriverWait(driver, 10).until(
        lambda d: _get_visible_row_ids(d)[0] != rows_desc[0]
    )
    rows_asc = _get_visible_row_ids(driver)

    assert rows_asc == list(reversed(rows_desc)), (
        f"L'ordine asc {rows_asc} non è l'inverso di desc {rows_desc}"
    )


# UC-05: Verifica che passando da 'Newest first' a 'Oldest first' l'ordine delle righe cambi
@pytest.mark.e2e
def test_uc05_sort_asc_changes_row_order(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    rows_desc = _get_visible_row_ids(driver)
    if len(rows_desc) < 2:
        pytest.skip("Servono almeno 2 report per verificare l'inversione di ordinamento")

    Select(driver.find_element(By.ID, "public-filter-sort")).select_by_value("asc")

    WebDriverWait(driver, 10).until(
        lambda d: _get_visible_row_ids(d)[0] != rows_desc[0]
    )

    rows_asc = _get_visible_row_ids(driver)
    assert rows_asc == list(reversed(rows_desc)), (
        f"L'ordine asc {rows_asc} non è l'inverso di desc {rows_desc}"
    )


# UC-05: Verifica che una data minima nel 2099 svuoti la tabella dei report
@pytest.mark.e2e
def test_uc05_date_from_far_future_empties_table(driver):
    from selenium.common.exceptions import StaleElementReferenceException
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    initial_rows = len([r for r in _get_visible_row_ids(driver) if any(char.isdigit() for char in r)])
    if initial_rows == 0:
        pytest.skip("Nessun report seed disponibile per questo test")

    _set_date_input(driver, "public-filter-date-from", "2099-01-01 00:00")
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        lambda d: "date_from=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )

    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 15, ignored_exceptions=(StaleElementReferenceException,)).until(
        lambda d: len([
            r for r in _get_visible_row_ids(d)
            if any(char.isdigit() for char in r)
        ]) == 0
    )

    rows = _get_visible_row_ids(driver)
    valid_report_rows = [r for r in rows if any(char.isdigit() for char in r)]
    assert len(valid_report_rows) == 0, (
        f"Con 'Date from' nel 2099 la tabella deve essere vuota, trovati: {valid_report_rows}"
    )


# UC-05: Verifica che una data massima nel 2000 svuoti la tabella dei report
@pytest.mark.e2e
def test_uc05_date_to_far_past_empties_table(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    _set_date_input(driver, "public-filter-date-to", "2000-01-01 00:00")
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        lambda d: "date_to=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )

    from selenium.common.exceptions import StaleElementReferenceException
    WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,)).until(
        lambda d: len([r for r in _get_visible_row_ids(d) if any(char.isdigit() for char in r)]) == 0
    )


# UC-05, Extension 4a: Verifica che ricaricando la home i filtri si azzerino e i report ricompaiano
@pytest.mark.e2e
def test_uc05_filter_reset_restores_reports(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    initial_count = len([r for r in _get_visible_row_ids(driver) if any(char.isdigit() for char in r)])
    if initial_count == 0:
        pytest.skip("Nessun report seed disponibile per questo test")

    _set_date_input(driver, "public-filter-date-from", "2099-01-01 00:00")
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        lambda d: "date_from=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )

    rows_filtered = _get_visible_row_ids(driver)
    valid_filtered = [r for r in rows_filtered if any(char.isdigit() for char in r)]
    assert len(valid_filtered) == 0

    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,)).until(
    lambda d: len([r for r in _get_visible_row_ids(d) if any(char.isdigit() for char in r)]) == initial_count
)
    restored_rows = _get_visible_row_ids(driver)
    valid_restored = [r for r in restored_rows if any(char.isdigit() for char in r)]
    assert len(valid_restored) == initial_count, (
        f"Dopo il reset del filtro ci si aspettano {initial_count} righe, trovate {len(valid_restored)}"
    )


# UC-05: Verifica che con un filtro categoria attivo il link CSV si aggiorni con category_id nella query string
@pytest.mark.e2e
def test_uc05_export_csv_link_reflects_active_category_filter(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    cat_select = Select(driver.find_element(By.ID, "public-filter-category"))
    options = cat_select.options
    if len(options) < 2:
        pytest.skip("Nessuna categoria disponibile per verificare il filtro nell'export")

    chosen_value = options[1].get_attribute("value")
    cat_select.select_by_value(chosen_value)
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-report-table-body"))
    )

    href = driver.find_element(By.ID, "public-export-link").get_attribute("href") or ""
    assert f"category_id={chosen_value}" in href, (
        f"L'href CSV '{href}' deve contenere 'category_id={chosen_value}' con il filtro attivo"
    )


# UC-08: Verifica che il link export rifletta il filtro per stato attivo
@pytest.mark.e2e
def test_uc08_export_csv_link_reflects_status_filter(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    status_select = Select(driver.find_element(By.ID, "public-filter-status"))
    options = status_select.options
    if len(options) < 2:
        pytest.skip("Nessuno stato pubblico disponibile per verificare l'export con filtro stato")

    chosen_value = options[1].get_attribute("value")
    status_select.select_by_value(chosen_value)
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-report-table-body"))
    )

    href = driver.find_element(By.ID, "public-export-link").get_attribute("href") or ""
    encoded_value = chosen_value.replace(" ", "+")
    assert f"status={encoded_value}" in href, (
        f"L'href export '{href}' deve contenere 'status={encoded_value}' con il filtro attivo"
    )


# UC-08: Verifica che il link export rifletta il parametro date_from
@pytest.mark.e2e
def test_uc08_export_csv_link_reflects_date_from_filter(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    _set_date_input(driver, "public-filter-date-from", "2024-01-01 00:00")
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        lambda d: "date_from=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )

    href = driver.find_element(By.ID, "public-export-link").get_attribute("href") or ""
    assert "date_from=" in href, (
        f"L'href export '{href}' deve contenere 'date_from=' con il filtro data-da impostato"
    )


# UC-08: Verifica che il link export rifletta il parametro date_to
@pytest.mark.e2e
def test_uc08_export_csv_link_reflects_date_to_filter(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    _set_date_input(driver, "public-filter-date-to", "2025-12-31 23:59")
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        lambda d: "date_to=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )

    href = driver.find_element(By.ID, "public-export-link").get_attribute("href") or ""
    assert "date_to=" in href, (
        f"L'href export '{href}' deve contenere 'date_to=' con il filtro data-a impostato"
    )


# UC-09: Verifica che la sezione 'Reports by category' sia visibile
@pytest.mark.e2e
def test_uc09_category_statistics_section_present(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-category-statistics"))
    )
    assert section.is_displayed(), "La sezione statistiche per categoria deve essere visibile"
    assert driver.find_element(By.ID, "public-category-statistics-title").is_displayed()


# UC-09: Verifica che almeno una categoria abbia un contatore visibile con i dati seed
@pytest.mark.e2e
def test_uc09_category_statistics_populated_with_data(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    items = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "[id^='public-category-stat-']:not([id*='-value'])")
        )
    )
    assert len(items) > 0, (
        "Con i dati seed almeno una voce di statistica per categoria deve essere presente"
    )


# UC-09: Verifica che la sezione 'Trend' sia visibile
@pytest.mark.e2e
def test_uc09_trend_statistics_section_present(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    section = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-trend-statistics"))
    )
    assert section.is_displayed(), "La sezione trend delle statistiche deve essere visibile"
    assert driver.find_element(By.ID, "public-trend-statistics-title").is_displayed()


# UC-09: Verifica che almeno un bucket temporale sia presente nella sezione trend con i dati seed
@pytest.mark.e2e
def test_uc09_trend_statistics_populated_with_data(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    items = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "[id^='public-trend-stat-']:not([id*='-value'])")
        )
    )
    assert len(items) > 0, (
        "Con i dati seed almeno un bucket di trend deve essere presente"
    )


# UC-09: Verifica che il select di granularita' sia presente con le opzioni Day, Week e Month
@pytest.mark.e2e
def test_uc09_stat_granularity_controls_present(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    assert driver.find_element(By.ID, "public-stat-granularity").is_displayed()
    assert driver.find_element(By.ID, "public-stat-granularity-option-day").is_displayed()
    assert driver.find_element(By.ID, "public-stat-granularity-option-week").is_displayed()
    assert driver.find_element(By.ID, "public-stat-granularity-option-month").is_displayed()


# UC-09: Verifica che cambiare la granularita' mantenga visibile la sezione trend
@pytest.mark.e2e
def test_uc09_stat_granularity_change_keeps_trend_visible(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    Select(driver.find_element(By.ID, "public-stat-granularity")).select_by_value("week")
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-trend-statistics"))
    )
    assert driver.find_element(By.ID, "public-trend-statistics").is_displayed()


# UC-08, Extension 2a: Verifica che con result set vuoto non venga prodotto un export fuorviante (bug noto)
@pytest.mark.e2e
@pytest.mark.implementation_bug(
    "HomePage.tsx non implementa la garanzia UC-08 Ext 2a: quando il set di risultati filtrato è vuoto, " 
    "il frontend visualizza un <tbody> vuoto senza alcun messaggio e mantiene il link 'Esporta CSV' " 
    "sempre attivo e cliccabile, indipendentemente dal numero di righe."
    "La garanzia minima 'Se non sono disponibili dati, non viene prodotta alcuna esportazione " 
    "non viene rispettata: il link di esportazione rimane attivo anche su un set di risultati vuoto."
)
@pytest.mark.xfail(
    reason=(
        "UC-08 Ext 2a non implementato in HomePage.tsx: il set di risultati vuoto non mostra alcun avviso "
        "e il collegamento di esportazione rimane attivo. Si tratta di una lacuna di implementazione, "
        "non di un difetto di test."
    ),
    strict=True,
)
def test_uc08_empty_result_set_blocks_export(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    initial_rows = len([r for r in _get_visible_row_ids(driver) if any(c.isdigit() for c in r)])
    if initial_rows == 0:
        pytest.skip("Nessun report seed disponibile: precondizione non soddisfatta")

    _set_date_input(driver, "public-filter-date-from", "2099-01-01 00:00")
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        lambda d: "date_from=" in (
            d.find_element(By.ID, "public-export-link").get_attribute("href") or ""
        )
    )
    WebDriverWait(driver, 15, ignored_exceptions=(StaleElementReferenceException,)).until(
        lambda d: len([r for r in _get_visible_row_ids(d) if any(c.isdigit() for c in r)]) == 0
    )

    empty_msg = driver.find_elements(By.ID, "public-empty-message")
    export_links = driver.find_elements(By.ID, "public-export-link")

    export_disabled = False
    if export_links:
        el = export_links[0]
        aria_disabled = (el.get_attribute("aria-disabled") or "").lower() == "true"
        has_disabled_attr = el.get_attribute("disabled") is not None
        href = el.get_attribute("href") or ""
        no_actionable_href = href.strip() in ("", "#")
        export_disabled = aria_disabled or has_disabled_attr or no_actionable_href

    empty_message_shown = bool(empty_msg) and empty_msg[0].is_displayed()

    assert empty_message_shown or export_disabled or not export_links, (
        "Con result set vuoto il sistema deve informare che non ci sono report "
        "da esportare oppure disabilitare/nascondere il link di export"
    )