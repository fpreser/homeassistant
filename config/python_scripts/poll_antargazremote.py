from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import datetime
import json
import os
import sys
import logging
import time
import re

# ==================== CONFIGURATION ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Décommente pour exécution sans fenêtre
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--lang=fr")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)

# Ajouts pour désactiver les erreurs GCM/notifications (basés sur des solutions testées)
options.add_argument("--disable-notifications")  # Désactive les notifications push
options.add_argument("--disable-background-timer-throttling")  # Évite les throttlings liés aux services background
options.add_argument("--disable-backgrounding-occluded-windows")  # Désactive les services background
options.add_argument("--disable-renderer-backgrounding")  # Désactive le background rendering
options.add_argument("--disable-client-side-phishing-detection")  # Désactive les services de sécurité Google
options.add_argument("--disable-component-update")  # Désactive les mises à jour de composants (inclut GCM)
options.add_argument("--disable-default-apps")  # Désactive les apps par défaut qui utilisent GCM
options.add_argument("--disable-extensions")  # Désactive les extensions qui pourraient déclencher GCM
options.add_argument("--disable-sync")  # Désactive la synchronisation Google (source d'authentification GCM)
options.add_argument("--disable-cloud-import")  # Désactive l'import cloud
options.add_argument("--metrics-recording-only")  # Limite les logs à la métrique, réduit les erreurs
options.add_argument("--mute-audio")  # Évite les erreurs liées aux médias (parfois couplées à GCM)
options.add_argument("--no-default-browser-check")  # Évite les checks qui déclenchent des services Google
options.add_argument("--no-first-run")  # Évite le premier lancement qui initialise GCM
options.add_argument("--disable-features=TranslateUI")  # Désactive des features qui utilisent GCM
options.add_argument("--disable-ipc-flooding-protection")  # Évite les protections IPC liées aux erreurs de connexion

# Pour fonctionner en local
# driver = webdriver.Chrome(options=options)


# Selenium Hub configuration début
options.add_argument("--headless=new")  # Headless mode for Docker
SELENIUM_HUB_URL = "http://192.168.1.10:4444/wd/hub"
# Connect to Selenium Hub
driver = webdriver.Remote(
    command_executor=SELENIUM_HUB_URL,
    options=options
)
# Selenium Hub configuration fin


# ==================== SCRIPT PRINCIPAL ====================
try:
    url = "https://my.antargaz.be"
    logger.info(f"Accès à {url}")
    driver.get(url)

    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    logger.info(f"Page chargée : {driver.current_url}")

    # --- Supprimer les overlays éventuels ---
    try:
        driver.execute_script("""
            const overlays = Array.from(document.querySelectorAll('div, section, dialog'))
                .filter(e => getComputedStyle(e).position === 'fixed' && parseInt(getComputedStyle(e).zIndex) > 1000);
            overlays.forEach(e => e.remove());
        """)
        logger.info("Suppression des overlays effectuée.")
    except Exception as e:
        logger.warning(f"Échec suppression overlays : {e}")

    # --- Trouver le bouton de connexion ---
    logger.info("Recherche du bouton de connexion...")
    login_button = None
    selectors = [
        (By.ID, "logAccount"),
        (By.XPATH, "//input[@value='Accéder à MonAntargaz']"),
        (By.XPATH, "//input[contains(@value, 'MonAntargaz')]")
    ]
    for by, sel in selectors:
        try:
            login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, sel)))
            logger.info(f"Bouton de connexion trouvé : {sel}")
            break
        except TimeoutException:
            continue
    if not login_button:
        raise NoSuchElementException("Bouton de connexion introuvable")

    # --- Clic sur le bouton ---
    try:
        login_button.click()
        logger.info("Clic normal sur le bouton de connexion.")
    except Exception:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();", login_button)
        logger.info("Clic via JS sur le bouton de connexion.")

    time.sleep(2)
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[-1])
        logger.info(f"Changement vers la nouvelle fenêtre : {driver.current_url}")

    # --- Attente du formulaire ---
    logger.info("Attente du formulaire de connexion...")
    WebDriverWait(driver, 20).until(
        EC.any_of(
            EC.presence_of_element_located((By.ID, "username")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")),
            EC.url_contains("login")
        )
    )

    # --- Passage iframe si besoin ---
    try:
        iframe = driver.find_element(By.CSS_SELECTOR, "iframe")
        driver.switch_to.frame(iframe)
        logger.info("Passage dans l'iframe de login.")
    except NoSuchElementException:
        logger.info("Pas d'iframe, on reste dans le contexte principal.")

    # --- Authentification ---
    if len(sys.argv) >= 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        username = os.getenv("ANTARGAZ_USERNAME")
        password = os.getenv("ANTARGAZ_PASSWORD")

    if not username or not password:
        try:
            import yaml
            with open("/config/secrets.yaml", "r") as f:
                secrets = yaml.safe_load(f)
            username = secrets.get("antargaz_username")
            password = secrets.get("antargaz_password")
            if username is not None:
                username = str(username)
            if password is not None:
                password = str(password)
        except Exception as e:
            logger.warning(f"Impossible de lire /config/secrets.yaml : {e}")

    if not username or not password:
        raise ValueError("Credentials manquants : passer ANTARGAZ_USERNAME/ANTARGAZ_PASSWORD en variables d'environnement, en arguments, ou dans /config/secrets.yaml")

    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys(password)
    driver.find_element(By.ID, "login_client").click()
    logger.info("Formulaire de connexion soumis.")

    # --- Attente post-login ---
    logger.info("Attente de la redirection post-login...")
    WebDriverWait(driver, 60).until(
        EC.any_of(
            EC.presence_of_element_located((By.ID, "gotoorder")),
            EC.presence_of_element_located((By.ID, "confirmgoback")),
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Consommation')]")),
            EC.url_contains("monantargaz")
        )
    )

    # --- Extraction des données de la page d'accueil ---
    logger.info("Extraction des données de la page d'accueil...")
    data = {
        "client": None,
        "solde_restant": None,
        "montant_echu": None,
        "derniere_facture": None,
        "adresse": None,
        "numero_citerne": None,
        "niveau": None,
        "date_lecture": None,
        "date_derniere_livraison": None,
        "volume_citerne": None,
        "type_gaz": None,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        # Numéro de client
        client_element = driver.find_element(By.XPATH, "//div[@id='welcom']//b")
        data["client"] = client_element.text.strip()
        logger.info(f"Numéro de client : {data['client']}")

        # Solde restant
        solde_element = driver.find_element(By.ID, "balancehome")
        data["solde_restant"] = solde_element.text.strip()
        logger.info(f"Solde restant : {data['solde_restant']}")

        # Montant échu
        montant_echu_element = driver.find_element(By.XPATH, "//div[@id='accountsituation']//b[2]")
        data["montant_echu"] = montant_echu_element.text.strip()
        logger.info(f"Montant échu : {data['montant_echu']}")

        # Dernière facture
        facture_element = driver.find_element(By.XPATH, "//div[@id='accountsituation']//b[3]")
        facture_date = driver.find_element(By.XPATH, "//div[@id='accountsituation']//b[4]").text.strip()
        data["derniere_facture"] = f"{facture_element.text.strip()} {facture_date}"
        logger.info(f"Dernière facture : {data['derniere_facture']}")

        # Adresse
        selected_contract = driver.find_element(By.ID, "selectedcontract")
        adresse_lines = selected_contract.text.split("\n")
        adresse = ", ".join(line.strip() for line in adresse_lines if line.strip() and "Citerne" not in line and "Site de livraison sélectionné" not in line)
        data["adresse"] = adresse
        logger.info(f"Adresse : {data['adresse']}")

        # Numéro de citerne
        citerne_element = driver.find_element(By.XPATH, "//div[@id='selectedcontract']//b")
        data["numero_citerne"] = citerne_element.text.strip()
        logger.info(f"Numéro de citerne : {data['numero_citerne']}")

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des données : {e}")
        driver.save_screenshot("erreur_extraction.png")
        with open("page_source_extraction.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

    # --- Naviguer vers la page Consommation ---
    logger.info("Navigation vers la page Consommation...")
    get_url = driver.current_url
    logger.info(f"Navigating to {get_url.split('#')[0]}#Consumption")
    driver.get(f"{get_url.split('#')[0]}#Consumption")

    # --- Attente du tableau de bord consommation ---
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "valueGauge")))
        logger.info("Page 'Consommation' chargée avec succès.")
    except TimeoutException:
        logger.error("⏱ Timeout : la page 'Consommation' ne s'est pas chargée.")
        driver.save_screenshot("timeout_consommation.png")
        with open("page_source_timeout.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise

    # --- Lecture du niveau de jauge, date de lecture et autres données ---
    logger.info("Lecture du niveau de jauge, date de lecture et autres données...")
    try:
        # Extraire niveau et date de lecture
        valueGauge = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "valueGauge"))
        ).get_attribute("value")
        date_lecture = driver.find_element(By.ID, "gaugecaldate").get_attribute("value")
        data["niveau"] = float(valueGauge) if valueGauge else None
        data["date_lecture"] = date_lecture if date_lecture else None
        logger.info(f"Niveau détecté : {data['niveau']}%")
        logger.info(f"Date de lecture : {data['date_lecture']}")

        # Extraire date_derniere_livraison, volume_citerne, type_gaz
        inputs = driver.find_elements(By.CSS_SELECTOR, "input.consoInputRead.inputnormal:not(#gaugecaldate)")
        for input_elem in inputs:
            value = input_elem.get_attribute("value")
            if not value:
                continue
            # Vérifier si c'est une date (format DD/MM/YYYY) pour date_derniere_livraison
            if re.match(r"^\d{2}/\d{2}/\d{4}$", value) and data["date_derniere_livraison"] is None:
                data["date_derniere_livraison"] = value
                logger.info(f"Date de la dernière livraison : {data['date_derniere_livraison']}")
            # Vérifier si c'est un nombre (volume_citerne)
            elif value.replace(".", "").isdigit() and data["volume_citerne"] is None:
                data["volume_citerne"] = float(value)
                logger.info(f"Volume de la citerne : {data['volume_citerne']}")
            # Sinon, c'est probablement le type de gaz
            elif not re.match(r"^\d{2}/\d{2}/\d{4}$", value) and not value.replace(".", "").isdigit() and data["type_gaz"] is None:
                data["type_gaz"] = value
                logger.info(f"Type de gaz : {data['type_gaz']}")

        # Vérifier si toutes les données ont été trouvées
        if data["date_derniere_livraison"] is None:
            logger.warning("Champ date_derniere_livraison introuvable.")
        if data["volume_citerne"] is None:
            logger.warning("Champ volume_citerne introuvable.")
        if data["type_gaz"] is None:
            logger.warning("Champ type_gaz introuvable.")

    except Exception as e:
        logger.error(f"Erreur lecture jauge ou autres données : {e}")
        data["niveau"] = None
        data["date_lecture"] = None
        data["date_derniere_livraison"] = None
        data["volume_citerne"] = None
        data["type_gaz"] = None
        driver.save_screenshot("erreur_jauge.png")
        with open("page_source_jauge.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

    # --- Sauvegarde dans le JSON ---
    with open("gas_tank_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info(f"💾 Données sauvegardées : {data}")
    logger.info(f"Fichier écrit : {os.path.join(os.getcwd(), 'gas_tank_data.json')}")

    # --- Imprimer le JSON pour Home Assistant ---
    print(json.dumps(data, indent=4))
    logger.info(f"💾 Données envoyées à stdout : {data}")

except Exception as e:
    logger.error(f"Erreur pendant l'exécution : {e}", exc_info=True)
    # Imprimer un JSON vide ou avec erreur pour Home Assistant
    print(json.dumps({"error": str(e)}))
finally:
    driver.quit()