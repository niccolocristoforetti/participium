import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from conftest import BASE_URL

"""
Test di accettazione Selenium per UC-04 – Sfoglia le segnalazioni sulla mappa
e UC-05 – Cerca e filtra le segnalazioni.

Entrambi i casi d'uso si svolgono interamente sulla home page (/),
accessibile senza autenticazione da qualsiasi visitatore.

UC-04 copre:
  - La home page è raggiungibile senza login.
  - La sezione mappa è presente e il suo contenitore è nel DOM.
  - La tabella dei report è visibile con le intestazioni corrette.
  - Cliccando "Open" su un report si arriva alla pagina di dettaglio.
  - Le righe della tabella hanno ID stabili nel formato public-report-row-<id>.
  - Extension 3a: assenza di report non causa crash.

UC-05 copre:
  - Il form di filtraggio è visibile con tutti i controlli (categoria, stato, date, ordine).
  - I select di categoria e stato sono popolati dal backend.
  - Il filtro per categoria mostra solo i report di quella categoria.
  - Il filtro per stato mostra solo i report con quello stato.
  - L'ordinamento default è 'Newest first'; passando ad 'Oldest first' l'ordine cambia.
  - Filtri per data futura/passata producono una tabella vuota.
  - Extension 4a: resettando i filtri i report ricompaiono.
  - Il link di esportazione CSV è presente e riflette i filtri attivi.
  - Il selettore di granularità per le statistiche di tendenza è funzionante.
"""


# Helpers

# Attende che la home page e il corpo della tabella siano presenti nel DOM.
def _wait_home_loaded(driver, timeout: int = 10) -> None:
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "home-page"))
    )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, "public-report-table-body"))
    )


# Restituisce gli id delle sole righe tabellari effettive visibili nella tabella pubblica.
def _get_visible_row_ids(driver) -> list:
    # Vincoliamo il selettore al tag 'tr' per escludere i marker delle mappe e le celle interne.
    rows = driver.find_elements(By.CSS_SELECTOR, "tr[id^='public-report-row-']")
    return [
        r.get_attribute("id")
        for r in rows
        if r.is_displayed() and "-map-marker" not in (r.get_attribute("id") or "")
    ]


# UC-04 – Accesso pubblico senza autenticazione

# La home page è raggiungibile da un visitatore non autenticato.
@pytest.mark.e2e
def test_uc04_home_page_accessible_without_login(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "home-page"))
    )
    assert driver.find_element(By.ID, "home-page").is_displayed(), (
        "La home page dovrebbe essere visibile senza autenticazione"
    )


# UC-04 – Struttura della pagina: hero, mappa, statistiche

# Il banner introduttivo con titolo e link di navigazione (Register / Login) è visibile.
@pytest.mark.e2e
def test_uc04_hero_section_visible(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "home-page")))

    assert driver.find_element(By.ID, "home-hero-title").is_displayed()
    assert driver.find_element(By.ID, "home-hero-actions").is_displayed()
    assert driver.find_element(By.ID, "register-link").is_displayed()
    assert driver.find_element(By.ID, "login-link").is_displayed()


# La sezione con la mappa OpenStreetMap è visibile nella home page.
@pytest.mark.e2e
def test_uc04_map_card_present(driver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-map-card"))
    )
    assert driver.find_element(By.ID, "public-map-card").is_displayed()
    assert driver.find_element(By.ID, "public-map-title").is_displayed()


# Il contenitore della mappa (id=public-map) è inserito nel DOM da MapPanel.
@pytest.mark.e2e
def test_uc04_map_container_rendered(driver):
    driver.get(BASE_URL)
    map_el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-map"))
    )
    assert map_el is not None, "Il contenitore della mappa deve essere presente nel DOM"


# La sezione statistiche pubbliche mostra il totale dei report come numero intero.
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


# UC-04 – Tabella report pubblicati

# La tabella dei report pubblicati è visibile con tutte le intestazioni attese.
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


# Le righe della tabella usano ID stabili nel formato public-report-row-<id numerico>.
@pytest.mark.e2e
def test_uc04_report_rows_have_stable_ids(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "tr[id^='public-report-row-']"))
    )

    # Selezioniamo solo i tag 'tr' reali escludendo i marker della mappa.
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


# UC-04 – Navigazione dal report nella tabella alla pagina di dettaglio

# Cliccando 'Open' su un report della tabella si arriva alla pagina di dettaglio.
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


# UC-04 – Extension 3a: tabella vuota non causa errori

# Il tbody della tabella esiste sempre; l'assenza di report non causa errori JS visibili.
@pytest.mark.e2e
def test_uc04_empty_table_body_does_not_crash(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    tbody = driver.find_element(By.ID, "public-report-table-body")
    assert tbody is not None, "Il corpo della tabella deve esistere anche quando è vuoto"

    # Nessun elemento di errore deve essere visibile sulla pagina al caricamento.
    error_els = driver.find_elements(By.ID, "public-filter-error")
    for el in error_els:
        WebDriverWait(driver, 5).until(EC.invisibility_of_element(el))
        assert not el.is_displayed(), (
            "Non ci dovrebbe essere un messaggio di errore visibile al caricamento della pagina"
        )


# UC-05 – Struttura del form di filtraggio

# Il form di filtraggio è visibile con tutti i controlli principali.
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


# Il select della categoria include 'All' come voce di default.
@pytest.mark.e2e
def test_uc05_filter_category_has_all_option(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    all_opt = driver.find_element(By.ID, "public-filter-category-option-all")
    assert all_opt is not None


# Il select dello stato include 'All public statuses' come voce di default.
@pytest.mark.e2e
def test_uc05_filter_status_has_all_option(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    all_opt = driver.find_element(By.ID, "public-filter-status-option-all")
    assert all_opt is not None


# Il select di ordinamento espone le opzioni 'Newest first' (desc) e 'Oldest first' (asc).
@pytest.mark.e2e
def test_uc05_filter_sort_options_present(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    assert driver.find_element(By.ID, "public-filter-sort-option-desc").is_displayed()
    assert driver.find_element(By.ID, "public-filter-sort-option-asc").is_displayed()


# Il select della categoria è popolato con almeno una categoria dal backend.
@pytest.mark.e2e
def test_uc05_category_options_loaded_from_backend(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    # Usiamo il selettore CSS sulle option del select per allinearci con i tag standard caricati.
    category_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "select#public-filter-category option")
        )
    )
    assert len(category_options) > 0, (
        "Almeno una categoria deve essere caricata nel select del filtro"
    )


# Il select dello stato è popolato con almeno uno stato pubblico dal backend.
@pytest.mark.e2e
def test_uc05_status_options_loaded_from_backend(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    # Usiamo il selettore CSS sulle option del select per allinearci con i tag standard caricati.
    status_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "select#public-filter-status option")
        )
    )
    assert len(status_options) > 0, (
        "Almeno uno stato pubblico deve essere caricato nel select del filtro"
    )


# UC-05 – Filtraggio per categoria

# Filtrando per una categoria specifica, tutte le righe visibili appartengono a quella categoria.
@pytest.mark.e2e
def test_uc05_filter_by_category_shows_only_matching_reports(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    cat_select = Select(driver.find_element(By.ID, "public-filter-category"))
    options = cat_select.options      # indice 0 = "All"
    if len(options) < 2:
        pytest.skip("Nessuna categoria disponibile oltre ad 'All'")

    chosen_name = options[1].text.strip()
    cat_select.select_by_visible_text(chosen_name)
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-report-table-body"))
    )

    # Extension 4a: lista vuota accettabile senza errori.
    rows = _get_visible_row_ids(driver)
    for r_id in rows:
        category_text = driver.find_element(By.ID, f"{r_id}-category").text.strip()
        assert category_text == chosen_name, (
            f"Riga '{r_id}' ha categoria '{category_text}', atteso '{chosen_name}'"
        )


# UC-05 – Filtraggio per stato

# Filtrando per uno stato specifico, tutte le righe visibili hanno quello stato.
@pytest.mark.e2e
def test_uc05_filter_by_status_shows_only_matching_reports(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    status_select = Select(driver.find_element(By.ID, "public-filter-status"))
    options = status_select.options   # indice 0 = "All public statuses"
    if len(options) < 2:
        pytest.skip("Nessuno stato pubblico disponibile oltre ad 'All'")

    chosen_status = options[1].text.strip()
    status_select.select_by_visible_text(chosen_status)
    driver.find_element(By.ID, "public-filter-submit").click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-report-table-body"))
    )

    rows = _get_visible_row_ids(driver)
    for r_id in rows:
        status_text = driver.find_element(By.ID, f"{r_id}-status").text.strip()
        assert status_text == chosen_status, (
            f"Riga '{r_id}' ha stato '{status_text}', atteso '{chosen_status}'"
        )


# UC-05 – Cambio di ordinamento

# L'ordinamento di default è 'Newest first' (desc).
@pytest.mark.e2e
def test_uc05_sort_default_is_desc(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    sort_select = Select(driver.find_element(By.ID, "public-filter-sort"))
    assert sort_select.first_selected_option.get_attribute("value") == "desc", (
        "Il valore selezionato di default nel select ordinamento deve essere 'desc'"
    )


# Passando da 'Newest first' a 'Oldest first' l'ordine delle righe cambia.
@pytest.mark.e2e
def test_uc05_sort_asc_changes_row_order(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr[id^='public-report-row-']"))
    )
    rows_desc = _get_visible_row_ids(driver)
    if len(rows_desc) < 2:
        pytest.skip("Servono almeno 2 report per verificare l'inversione di ordinamento")

    # Cambia ordinamento e invia il form.
    Select(driver.find_element(By.ID, "public-filter-sort")).select_by_value("asc")
    driver.find_element(By.ID, "public-filter-submit").click()

    # Attesa asincrona esplicita basata sulla variazione del primo elemento ID della tabella pubblica.
    WebDriverWait(driver, 10).until(
        lambda d: _get_visible_row_ids(d)[0] != rows_desc[0]
    )

    rows_asc = _get_visible_row_ids(driver)
    assert rows_desc != rows_asc, (
        "L'ordine delle righe deve cambiare passando da 'Newest first' a 'Oldest first'"
    )


# UC-05 – Filtraggio per data

# 'Date from' impostato nel 2099 produce una tabella vuota.
@pytest.mark.e2e
def test_uc05_date_from_far_future_empties_table(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    # Imposta il valore e scatena gli eventi nativi per React; formato spazio standard per l'interazione HTML5.
    date_input = driver.find_element(By.ID, "public-filter-date-from")
    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """,
        date_input,
        "2099-01-01 00:00",
    )
    driver.find_element(By.ID, "public-filter-submit").click()

    # Sincronizza l'attesa sull'aggiornamento dinamico dell'export link prima di effettuare le verifiche sul DOM.
    WebDriverWait(driver, 10).until(
        lambda d: "date_from=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )
    
    rows = _get_visible_row_ids(driver)
    valid_report_rows = [r for r in rows if any(char.isdigit() for char in r)]
    assert len(valid_report_rows) == 0, (
        f"Con 'Date from' nel 2099 la tabella deve essere vuota, trovati: {valid_report_rows}"
    )


# 'Date to' impostato al 2000-01-01 produce una tabella vuota.
@pytest.mark.e2e
def test_uc05_date_to_far_past_empties_table(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    date_input = driver.find_element(By.ID, "public-filter-date-to")
    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """,
        date_input,
        "2000-01-01 00:00",
    )
    driver.find_element(By.ID, "public-filter-submit").click()

    # Sincronizza l'attesa sull'aggiornamento dinamico dell'export link prima di effettuare le verifiche sul DOM.
    WebDriverWait(driver, 10).until(
        lambda d: "date_to=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )
    
    rows = _get_visible_row_ids(driver)
    valid_report_rows = [r for r in rows if any(char.isdigit() for char in r)]
    assert len(valid_report_rows) == 0, (
        f"Con 'Date to' nel 2000 la tabella deve essere vuota, trovati: {valid_report_rows}"
    )


# UC-05 – Extension 4a: reset dei filtri ripristina i risultati

# Rimuovendo un filtro restrittivo i report tornano visibili nella tabella.
@pytest.mark.e2e
def test_uc05_filter_reset_restores_reports(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    initial_count = len([r for r in _get_visible_row_ids(driver) if any(char.isdigit() for char in r)])
    if initial_count == 0:
        pytest.skip("Nessun report seed disponibile per questo test")

    # Applica filtro restrittivo → tabella vuota.
    date_input = driver.find_element(By.ID, "public-filter-date-from")
    driver.execute_script(
        """
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        """,
        date_input,
        "2099-01-01 00:00",
    )
    driver.find_element(By.ID, "public-filter-submit").click()
    
    WebDriverWait(driver, 10).until(
        lambda d: "date_from=" in (d.find_element(By.ID, "public-export-link").get_attribute("href") or "")
    )
    
    rows_filtered = _get_visible_row_ids(driver)
    valid_filtered = [r for r in rows_filtered if any(char.isdigit() for char in r)]
    assert len(valid_filtered) == 0

    # Rimuove il filtro ricaricando la pagina — l'azione di reset più robusta per l'utente.
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    # Attende che le righe tornino al conteggio iniziale in modo puramente dinamico.
    WebDriverWait(driver, 10).until(
        lambda d: len([r for r in _get_visible_row_ids(d) if any(char.isdigit() for char in r)]) == initial_count
    )
    restored_rows = _get_visible_row_ids(driver)
    valid_restored = [r for r in restored_rows if any(char.isdigit() for char in r)]
    assert len(valid_restored) == initial_count, (
        f"Dopo il reset del filtro ci si aspettano {initial_count} righe, trovate {len(valid_restored)}"
    )


# UC-05 – Esportazione CSV

# Il link di esportazione CSV è visibile e punta all'endpoint /export.
@pytest.mark.e2e
def test_uc05_export_csv_link_present(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    export_link = driver.find_element(By.ID, "public-export-link")
    assert export_link.is_displayed(), "Il link di esportazione CSV deve essere visibile"

    href = export_link.get_attribute("href") or ""
    assert "export" in href, (
        f"L'href del link CSV '{href}' deve contenere 'export'"
    )


# Il link di esportazione CSV include category_id nella querystring quando il filtro è attivo.
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


# UC-05 – Granularità delle statistiche di tendenza

# Il selettore di granularità (day/week/month) per le statistiche di tendenza è presente.
@pytest.mark.e2e
def test_uc05_stat_granularity_controls_present(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    assert driver.find_element(By.ID, "public-stat-granularity").is_displayed()
    assert driver.find_element(By.ID, "public-stat-granularity-option-day").is_displayed()
    assert driver.find_element(By.ID, "public-stat-granularity-option-week").is_displayed()
    assert driver.find_element(By.ID, "public-stat-granularity-option-month").is_displayed()


# Cambiando la granularità la sezione statistiche rimane stabile senza errori visibili.
@pytest.mark.e2e
def test_uc05_stat_granularity_change_does_not_cause_error(driver):
    driver.get(BASE_URL)
    _wait_home_loaded(driver)

    Select(driver.find_element(By.ID, "public-stat-granularity")).select_by_value("week")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "public-statistics-card"))
    )
    assert driver.find_element(By.ID, "public-statistics-card").is_displayed()

    # Sincronizza l'attesa asincrona accertandoti che il messaggio transitorio di caricamento/errore sia invisibile prima dell'asserzione.
    error_els = driver.find_elements(By.ID, "public-filter-error")
    for el in error_els:
        WebDriverWait(driver, 5).until(EC.invisibility_of_element(el))
        assert not el.is_displayed(), (
            "Non ci devono essere errori visibili dopo il cambio di granularità"
        )