import os
import random
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_KEY = os.getenv("ODDSAPI_KEY")  # TheOddsAPI

def calculate_bets(c1, c2):
    mise1 = round(random.uniform(5, 10), 2)
    mise2 = round((mise1 * c1) / c2, 2) if c2 else 0
    gain1 = round(mise1 * c1 - mise1 - mise2, 2)
    gain2 = round(mise2 * c2 - mise1 - mise2, 2)
    return mise1, mise2, gain1, gain2

def get_one_match():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=1x2&oddsFormat=decimal"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        for event in data:
            teams = f"{event['home_team']} vs {event['away_team']}"
            sites = event.get("bookmakers", [])
            if sites:
                odds = sites[0]["markets"][0]["outcomes"]
                c1 = next((o["price"] for o in odds if o["name"] == "Home"), None)
                c2 = next((o["price"] for o in odds if o["name"] == "Away"), None)
                start_time = event.get("commence_time", "??:??")
                link = sites[0].get("url", "")
                return (teams, c1, c2, start_time, link)
        return None
    except Exception as e:
        print("Erreur JSON :", e)
        return None

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    match = get_one_match()
    if match:
        teams, c1, c2, start_time, link = match
        mise1, mise2, gain1, gain2 = calculate_bets(c1, c2)
        message = f"""
Match trouvé ⚽
{teams}
Début : {start_time}

Cote 1 : {c1}
Cote 2 : {c2}

Mise 1 : {mise1} €
Mise 2 : {mise2} €

Gain si 1 gagne : {gain1} €
Gain si 2 gagne : {gain2} €

Lien : {link}
"""
    else:
        message = "Aucun match trouvé pour l'instant."
    await update.message.reply_text(message)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("scan", scan))
    print("Bot démarré… envoie /scan pour recevoir un match")
    app.run_polling()
