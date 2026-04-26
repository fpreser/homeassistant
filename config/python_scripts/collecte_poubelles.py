# /config/python_scripts/collecte_poubelles.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import date, timedelta
import datetime
import json
import os
import logging
import time
import re
import sys

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ==================== CONFIG SELENIUM ====================
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-notifications")
options.add_argument("--disable-extensions")
options.add_argument("--disable-sync")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-renderer-backgrounding")
options.add_argument("--disable-features=TranslateUI")
options.add_argument("--lang=fr")
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# Selenium Hub
SELENIUM_HUB_URL = "http://192.168.1.10:4444/wd/hub"
driver = webdriver.Remote(command_executor=SELENIUM_HUB_URL, options=options)

# ==================== CONFIG POUBELLES ====================
url = "https://www.messancy.be/messancy/collectedesdechets/detail?luid=0f527ebf-582a-4ca6-be69-59052e1da37f&zuid=Rue%20Jacques&zip=6782"
today = date.today()

keyword_to_attr = {
    "déchets organiques": "organiques",
    "ordures ménagères": "ordures",
    "résiduels": "ordures",
    "pmc": "pmc",
    "papier": "papier",
    "papiers-cartons": "papier"
}

# ==================== DONNÉES ====================
data = {
    "organiques": None,
    "ordures": None,
    "pmc": None,
    "papier": None,
    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# ==================== SCRIPT PRINCIPAL ====================
try:
    logger.info(f"Accès à {url}")
    driver.get(url)

    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    logger.info(f"Page chargée : {driver.current_url}")

    # --- Supprimer overlays ---
    try:
        driver.execute_script("""
            const overlays = Array.from(document.querySelectorAll('div, section, dialog'))
                .filter(e => getComputedStyle(e).position === 'fixed' && parseInt(getComputedStyle(e).zIndex) > 1000);
            overlays.forEach(e => e.remove());
        """)
        logger.info("Overlays supprimés.")
    except Exception as e:
        logger.warning(f"Échec suppression overlays : {e}")

    # --- Consentement ---
    try:
        accept = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accepter')]"))
        )
        accept.click()
        logger.info("Consentement accepté.")
        time.sleep(6)
    except Exception as e:
        logger.info("Pas de bandeau de consentement.")
        time.sleep(3)

    # --- Attente du calendrier ---
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".lgc-garbage-cell"))
        )
        logger.info("Calendrier chargé.")
        time.sleep(4)
    except TimeoutException:
        logger.error("Timeout : calendrier non chargé.")
        driver.save_screenshot("timeout_calendrier.png")
        raise

    # --- Parcours des cellules ---
    cells = driver.find_elements(By.CSS_SELECTOR, ".lgc-garbage-cell")
    logger.info(f"{len(cells)} cellules trouvées.")

    for i, cell in enumerate(cells):
        txt = cell.text.strip()
        txt_lower = txt.lower()
        logger.debug(f"Cellule {i+1}: {txt}")

        # === Parse date ===
        parsed_date = None
        if "demain" in txt_lower:
            parsed_date = today + timedelta(days=1)
            logger.info(f"Demain détecté → {parsed_date}")
        else:
            m = re.search(r'le\s*(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})', txt_lower)
            if m:
                day, month, year = int(m.group(1)), int(m.group(2)), 2000 + int(m.group(3))
                parsed_date = date(year, month, day)
                logger.info(f"Date Le JJ/MM/AA → {parsed_date}")

        if not parsed_date or parsed_date <= today:
            continue

        # === Chercher catégories ===
        for kw, attr in keyword_to_attr.items():
            if kw in txt_lower and data[attr] is None:
                data[attr] = parsed_date.strftime("%Y-%m-%d")
                logger.info(f"{attr.capitalize()} → {data[attr]}")

        if all(data[k] for k in ["organiques", "ordures", "pmc", "papier"]):
            logger.info("Toutes les catégories trouvées.")
            break

    # --- Sauvegarde JSON ---
    output_file = "/config/poubelles_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Données sauvegardées : {output_file}")

    # --- Sortie stdout pour HA ---
    print(json.dumps(data, ensure_ascii=False))
    logger.info("Données envoyées à stdout.")

except Exception as e:
    error_data = {"error": str(e), "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    logger.error(f"Erreur : {e}", exc_info=True)
    print(json.dumps(error_data))
    driver.save_screenshot("erreur_poubelles.png")
    with open("page_source_error.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

finally:
    driver.quit()