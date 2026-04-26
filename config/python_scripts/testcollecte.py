# python_scripts/collecte_poubelles.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
import time
import re

# ======================
# CONFIG
# ======================
url = "https://www.messancy.be/messancy/collectedesdechets/detail?luid=0f527ebf-582a-4ca6-be69-59052e1da37f&zuid=Rue%20Jacques&zip=6782"
categories = ["déchets organiques", "Ordures ménagères", "PMC", "Papier"]
today = date.today()

# Mots-clés → catégorie
keyword_to_category = {
    "déchets organiques": "déchets organiques",
    "ordures ménagères": "Ordures ménagères",
    "résiduels": "Ordures ménagères",
    "pmc": "PMC",
    "papier": "Papier",
    "papiers-cartons": "Papier"
}

# ======================
# SELENIUM HUB CONFIG
# ======================
SELENIUM_HUB_URL = "http://192.168.1.10:4444/wd/hub"

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Headless moderne (Chrome 109+)
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

# ======================
# DRIVER REMOTE
# ======================
driver = webdriver.Remote(
    command_executor=SELENIUM_HUB_URL,
    options=options
)

try:
    print("Connure: Connexion au Selenium Hub...")
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # === Consentement ===
    try:
        accept = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'accepter')]"))
        )
        accept.click()
        print("Consentement accepté.")
        time.sleep(6)
    except:
        print("Pas de bandeau de consentement.")
        time.sleep(3)

    # === Attente du calendrier ===
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".lgc-garbage-cell"))
    )
    time.sleep(4)

    cells = driver.find_elements(By.CSS_SELECTOR, ".lgc-garbage-cell")
    print(f"{len(cells)} cellules trouvées.")

    next_dates = {cat: None for cat in categories}

    for cell in cells:
        txt = cell.text.strip()
        txt_lower = txt.lower()

        # === Parse date ===
        parsed_date = None
        if "demain" in txt_lower:
            parsed_date = today + timedelta(days=1)
        else:
            # Format: "Le 19/11/25"
            m = re.search(r'le\s*(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})', txt_lower)
            if m:
                day, month, year = int(m.group(1)), int(m.group(2)), 2000 + int(m.group(3))
                parsed_date = date(year, month, day)

        if not parsed_date or parsed_date <= today:
            continue

        # === Chercher catégories ===
        for kw, cat in keyword_to_category.items():
            if kw in txt_lower and next_dates[cat] is None:
                next_dates[cat] = parsed_date

        if all(next_dates.values()):
            break

    # === Résultat ===
    print("\n" + "="*60)
    print(" " * 20 + "PROCHAINES COLLECTES")
    print("="*60)
    for cat in categories:
        val = next_dates[cat].strftime('%Y-%m-%d') if next_dates[cat] else "Non trouvée"
        print(f"{cat:25} → {val}")
    print("="*60)

finally:
    driver.quit()