import os
import time
import random
import requests

# Variables d'environnement sur Railway
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("ODDSAPI_KEY")  # Clé TheOddsAPI

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Erreur Telegram :", e)

def calculate_bets(c1, c2):
    mise1 = round(random.uniform(5, 10), 2)
    mise2 = round((mise1 * c1) / c2, 2) if c2 != 0 else 0
    gain1 = round(mise1 * c1 - mise1 - mise2, 2)
    gain2 = round(mise2 * c2 - mise1 - mise2, 2)
    return mise1, mise2, gain1, gain2

def get_live_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=1x2&oddsFormat=decimal"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        matches = []
        for event in data:
            teams = f"{event['home_team']} vs {event['away_team']}"
            sites = event.get("bookmakers", [])
            if sites:
                # On prend le premier bookmaker
                odds = sites[0]["markets"][0]["outcomes"]
                c1 = next((o["price"] for o in odds if o["name"] == "Home"), None)
                c2 = next((o["price"] for o in odds if o["name"] == "Draw"), None)
                c3 = next((o["price"] for o in odds if o["name"] == "Away"), None)
                start_time = event.get("commence_time", "??:??")
                link = sites[0].get("url", "")
                matches.append((teams, c1, c3, start_time, link))  # 1 et 2/away pour X2
        return matches
    except Exception as e:
        print("Erreur JSON :", e)
        return []

def main():
    sent_matches = set()
    while True:
        matches = get_live_matches()
        if matches:
            for match, c1, c2, start_time, link in matches:
                if match in sent_matches:
                    continue
                sent_matches.add(match)
                mise1, mise2, gain1, gain2 = calculate_bets(c1, c2)
                message = f"""
Match trouvé ⚽
{match}
Début : {start_time}

Cote 1 : {c1}
Cote X2 : {c2}

Mise 1 : {mise1} €
Mise X2 : {mise2} €

Gain si 1 gagne : {gain1} €
Gain si X2 gagne : {gain2} €

Lien : {link}
"""
                send_message(message)
        else:
            print("Aucun match pour l'instant.")
        time.sleep(60)  # vérifie toutes les 60s

if __name__ == "__main__":
    main()
