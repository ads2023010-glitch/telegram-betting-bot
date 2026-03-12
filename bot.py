import os
import time
import random
import requests

# Variables d'environnement sur Railway
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    """Envoie un message sur Telegram"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Erreur Telegram :", e)

def calculate_bets(c1, c2):
    """Calcule les mises pour un gain ±2€"""
    mise1 = round(random.uniform(5, 10), 2)
    mise2 = round((mise1 * c1) / c2, 2) if c2 != 0 else 0
    gain1 = round(mise1 * c1 - mise1 - mise2, 2)
    gain2 = round(mise2 * c2 - mise1 - mise2, 2)
    return mise1, mise2, gain1, gain2

def get_live_matches():
    """Récupère tous les matchs depuis le JSON Megapari"""
    url = "https://4689732mp.pro/service-api/LiveFeed/Get1x2_VZip?count=20&lng=fr&gr=824&mode=4&country=6&partner=192&virtualSports=true&countryFirst=true&noFilterBlockEvent=true"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        matches = []

        for event in data.get("Value", []):
            for e in event.get("E", []):
                # Nom des équipes
                teams = f"{e.get('O1','Equipe1')} vs {e.get('O2','Equipe2')}"
                # Récupère les cotes (1 et X2)
                if "C" in e and len(e["C"]) >= 1:
                    cotes = e["C"][0]
                    if len(cotes) >= 2:
                        c1 = float(cotes[0])
                        c2 = float(cotes[2]) if len(cotes) > 2 else float(cotes[1])
                        start_time = e.get("S", "??:??")
                        link = f"https://megapari.com/fr/live/football"
                        matches.append((teams, c1, c2, start_time, link))
        return matches
    except Exception as e:
        print("Erreur récupération JSON :", e)
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
            send_message("Aucun match trouvé pour l'instant.")  # permet de tester
            print("Aucun match pour l'instant.")
        time.sleep(30)

if __name__ == "__main__":
    main()
