import os
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Telegram
TOKEN = os.getenv("TOKEN")       # défini dans Railway comme variable d'environnement
CHAT_ID = os.getenv("CHAT_ID")   # défini dans Railway

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def calculate_bets(c1, c2):
    mise1 = round(random.uniform(5, 10), 2)
    mise2 = round((mise1 * c1) / c2, 2)
    gain1 = round(mise1 * c1 - mise1 - mise2, 2)
    gain2 = round(mise2 * c2 - mise1 - mise2, 2)
    return mise1, mise2, gain1, gain2

def get_live_matches():
    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    driver.get("https://www.megapari.com/fr/live/football")
    time.sleep(5)  # laisser le site se charger

    matches = []
    try:
        match_elements = driver.find_elements_by_css_selector(".event-row")  # à adapter selon le site
        for m in match_elements:
            teams = m.find_element_by_css_selector(".event-name").text
            odds_elements = m.find_elements_by_css_selector(".price-cell")
            if len(odds_elements) >= 2:
                c1 = float(odds_elements[0].text.replace(",", "."))
                c2 = float(odds_elements[1].text.replace(",", "."))
                matches.append((teams, c1, c2))
    except Exception as e:
        print("Erreur Selenium :", e)
    driver.quit()
    return matches

def main():
    sent_matches = set()
    while True:
        matches = get_live_matches()
        if matches:
            for match, c1, c2 in matches:
                if match in sent_matches:
                    continue
                sent_matches.add(match)
                mise1, mise2, gain1, gain2 = calculate_bets(c1, c2)
                message = f"""
Match trouvé ⚽
{match}

Cote 1 : {c1}
Cote X2 : {c2}

Mise 1 : {mise1} €
Mise X2 : {mise2} €

Gain si 1 gagne : {gain1} €
Gain si X2 gagne : {gain2} €

Lien : https://megapari.com/fr/live/football
"""
                send_message(message)
        else:
            print("Aucun match pour l'instant.")
        time.sleep(30)  # scan toutes les 30s

if __name__ == "__main__":
    main()

