"""
Test di accettazione Selenium per UC-03 – Invia segnalazione.

Copre lo scenario principale di successo e le estensioni documentate:
- la pagina del form è accessibile solo ai cittadini autenticati;
- tutti i campi obbligatori del form sono visibili ed è presente la sezione della mappa di localizzazione;
- una segnalazione valida può essere inviata e l'utente viene reindirizzato al dettaglio della segnalazione;
- la segnalazione appena creata appare nella lista della dashboard personale del cittadino;
- i campi obbligatori mancanti vengono bloccati al momento dell'invio;
- più di tre foto allegate mostrano un messaggio di errore (controllo lato client);
- la spunta anonima può essere attivata/disattivata e viene memorizzata correttamente.
"""

import os
import tempfile
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from conftest import BASE_URL, login_as



# Helpers

def _unique_title() -> str:
    return f"Selenium report {int(time.time() * 1000)}"

#Scrive una sequenza di byte JPEG minima e valida in un file temporaneo e ne restituisce il percorso.
def _make_temp_image(suffix: str = ".jpg") -> str:
    minimal_jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t"
        b"\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a"
        b"\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\x1e"
        b"\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00"
        b"\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b"
        b"\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04"
        b"\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa"
        b"\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br"
        b"\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZ"
        b"cdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95"
        b"\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3"
        b"\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca"
        b"\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7"
        b"\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa"
        b"\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd4P\x00\x00\x00\x1f\xff\xd9"
    )
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as fh:
        fh.write(minimal_jpeg)
    return path



# UC-03 – Controllo Accessi

# I visitatori non autenticati non possono raggiungere direttamente /reports/new.
@pytest.mark.e2e
def test_new_report_page_requires_authentication(driver):
    driver.get(f"{BASE_URL}/reports/new")
    # The ProtectedRoute should redirect away from /reports/new.
    WebDriverWait(driver, 10).until(lambda d: "/reports/new" not in d.current_url)
    assert "/reports/new" not in driver.current_url, (
        "Unauthenticated user should be redirected away from the report creation page"
    )



# UC-03 – struttura della pagina
#Il form di creazione segnalazione mostra tutti i campi richiesti dopo il login.
@pytest.mark.e2e
def test_new_report_page_loads(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/reports/new")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "new-report-page"))
    )
    assert driver.find_element(By.ID, "new-report-form").is_displayed()
    assert driver.find_element(By.ID, "report-title").is_displayed()
    assert driver.find_element(By.ID, "report-description").is_displayed()
    assert driver.find_element(By.ID, "report-category").is_displayed()
    assert driver.find_element(By.ID, "report-latitude").is_displayed()
    assert driver.find_element(By.ID, "report-longitude").is_displayed()
    assert driver.find_element(By.ID, "report-anonymous").is_displayed()
    assert driver.find_element(By.ID, "report-photos").is_displayed()
    assert driver.find_element(By.ID, "new-report-submit").is_displayed()

#La sezione della mappa per la selezione della posizione è presente nella pagina del form
@pytest.mark.e2e
def test_new_report_map_section_present(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/reports/new")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "new-report-map-section"))
    )
    assert driver.find_element(By.ID, "new-report-map-section").is_displayed()


# UC-03 – Flusso completo

#L'invio di una segnalazione valida reindirizza il cittadino alla pagina di dettaglio.
@pytest.mark.e2e
def test_new_report_submit_redirects_to_detail(driver):
    photo_path = _make_temp_image()
    try:
        login_as(driver, "citizen@example.com", "Citizen123!")
        driver.get(f"{BASE_URL}/reports/new")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "new-report-form"))
        )

        title = _unique_title()
        driver.find_element(By.ID, "report-title").clear()
        driver.find_element(By.ID, "report-title").send_keys(title)
        driver.find_element(By.ID, "report-description").clear()
        driver.find_element(By.ID, "report-description").send_keys(
            "Segnalazione di test automatizzata con Selenium, si prega di ignorare."
        )

        # Categoria: la prima opzione disponibile è pre-selezionata.

        # Posizione: i valori predefiniti (centro di Torino) sono già pre-compilati.

        # Allega una foto valida.
        driver.find_element(By.ID, "report-photos").send_keys(photo_path)

        driver.find_element(By.ID, "new-report-submit").click()

        # Il sistema crea la segnalazione e naviga verso la sua pagina di dettaglio.
        WebDriverWait(driver, 15).until(
            lambda d: "/reports/" in d.current_url and "/reports/new" not in d.current_url
        )
        assert "/reports/" in driver.current_url, (
            "Dopo l'invio il browser dovrebbe trovarsi sull'URL di dettaglio della segnalazione"
        )
    finally:
        os.unlink(photo_path)

#La segnalazione inviata appare nella lista delle segnalazioni personali del cittadino nella dashboard.
@pytest.mark.e2e
def test_new_report_appears_in_dashboard(driver):
    photo_path = _make_temp_image()
    try:
        login_as(driver, "citizen@example.com", "Citizen123!")
        driver.get(f"{BASE_URL}/reports/new")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "new-report-form"))
        )

        title = _unique_title()
        driver.find_element(By.ID, "report-title").clear()
        driver.find_element(By.ID, "report-title").send_keys(title)
        driver.find_element(By.ID, "report-description").clear()
        driver.find_element(By.ID, "report-description").send_keys("Dashboard visibility test.")
        driver.find_element(By.ID, "report-photos").send_keys(photo_path)
        driver.find_element(By.ID, "new-report-submit").click()

        WebDriverWait(driver, 15).until(
            lambda d: "/reports/" in d.current_url and "/reports/new" not in d.current_url
        )

        # Naviga nella dashboard e cerca il titolo della segnalazione.
        driver.get(f"{BASE_URL}/dashboard")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard-page"))
        )
        # Aspettiamo esplicitamente che il testo del titolo della nuova segnalazione compaia nella pagina
        WebDriverWait(driver, 10).until(
            lambda d: title in d.page_source,
            message=f"La segnalazione creata '{title}' non è comparsa asincronamente nella dashboard"
        )
        assert title in driver.page_source, (
            f"La segnalazione creata '{title}' non è stata trovata nella dashboard del cittadino"
        )
    finally:
        os.unlink(photo_path)

# UC-03 – Estensione: opzione anonima

#Una segnalazione contrassegnata come anonima può essere inviata senza errori."
@pytest.mark.e2e
def test_new_report_anonymous_flag_submits_successfully(driver):
    photo_path = _make_temp_image()
    try:
        login_as(driver, "citizen@example.com", "Citizen123!")
        driver.get(f"{BASE_URL}/reports/new")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "new-report-form"))
        )

        driver.find_element(By.ID, "report-title").clear()
        driver.find_element(By.ID, "report-title").send_keys(_unique_title() + " [anon]")
        driver.find_element(By.ID, "report-description").clear()
        driver.find_element(By.ID, "report-description").send_keys("Test di segnalazione anonima.")

        anon_checkbox = driver.find_element(By.ID, "report-anonymous")
        if not anon_checkbox.is_selected():
            anon_checkbox.click()
        assert anon_checkbox.is_selected(), "La casella anonima dovrebbe essere spuntata prima dell'invio"

        driver.find_element(By.ID, "report-photos").send_keys(photo_path)
        driver.find_element(By.ID, "new-report-submit").click()

        WebDriverWait(driver, 15).until(
            lambda d: "/reports/" in d.current_url and "/reports/new" not in d.current_url
        )
        assert "/reports/" in driver.current_url
    finally:
        os.unlink(photo_path)


# UC-03 – Estensione 6b: più di tre foto attivano l'errore lato client

@pytest.mark.e2e
def test_new_report_more_than_three_photos_shows_error(driver):
    #Caricare più di tre foto mostra un messaggio di errore lato client.
    photos = [_make_temp_image() for _ in range(4)]
    try:
        login_as(driver, "citizen@example.com", "Citizen123!")
        driver.get(f"{BASE_URL}/reports/new")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "new-report-form"))
        )

        driver.find_element(By.ID, "report-title").clear()
        driver.find_element(By.ID, "report-title").send_keys(_unique_title())
        driver.find_element(By.ID, "report-description").clear()
        driver.find_element(By.ID, "report-description").send_keys("Test per numero eccessivo di foto.")

        # send_keys("\n") per i percorsi uniti da un ritorno a capo per gli input di tipo file multipli
        driver.find_element(By.ID, "report-photos").send_keys(
            "\n".join(photos)
        )

        # Il controllo lato client si attiva subito dopo la selezione, quindi verifichiamo la presenza dell'elemento di errore.
        error = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "new-report-error"))
        )
        assert error.is_displayed(), "Messaggio di errore quando vengono selezionate più di 3 foto"
        # Solo 3 foto sono trattenute dal sistema.
        selected_count_el = driver.find_element(By.ID, "new-report-selected-photos")
        assert "3" in selected_count_el.text, (
            "Devono mantenersi solo 3 foto dopo averne selezionate 4"
        )
    finally:
        for p in photos:
            os.unlink(p)



# UC-03 – Estensione 6a: blocco dei campi obbligatori mancanti

#L'invio senza un titolo non crea la segnalazione (validazione del browser).
@pytest.mark.e2e
def test_new_report_missing_title_blocked(driver):
    login_as(driver, "citizen@example.com", "Citizen123!")
    driver.get(f"{BASE_URL}/reports/new")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "new-report-form"))
    )

    # Lascia il titolo vuoto e compila il resto.
    driver.find_element(By.ID, "report-title").clear()
    driver.find_element(By.ID, "report-description").send_keys("Descrizione senza titolo.")
    driver.find_element(By.ID, "new-report-submit").click()

    # L'attributo HTML `required` a livello di browser impedisce l'invio; l'URL non deve cambiare.
    assert "/reports/new" in driver.current_url, (
        "L'invio del form è bloccato quando il campo del titolo è vuoto"
    )