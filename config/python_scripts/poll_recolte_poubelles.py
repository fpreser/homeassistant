from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import datetime
import json
import os
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

# Pour fonctionner en local début
driver = webdriver.Chrome(options=options)
# Pour fonctionner en local début

# Pour fonctionner en docker début
  # Selenium Hub configuration début
  # options.add_argument("--headless=new")  # Headless mode for Docker
  # SELENIUM_HUB_URL = "http://192.168.1.10:4444/wd/hub"
  # Connect to Selenium Hub
  # driver = webdriver.Remote(
  #    command_executor=SELENIUM_HUB_URL,
  #    options=options
  # )
  # Selenium Hub configuration fin
# Pour fonctionner en docker fin

# ==================== SCRIPT PRINCIPAL ====================
try:
    url = "https://www.messancy.be/messancy/collectedesdechets/detail?luid=0f527ebf-582a-4ca6-be69-59052e1da37f&zuid=Rue%20Jacques&zip=6782"
    logger.info(f"Accès à {url}")
    driver.get(url)

    WebDriverWait(driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")
    logger.info(f"Page chargée : {driver.current_url}")
    
finally:
    driver.quit()