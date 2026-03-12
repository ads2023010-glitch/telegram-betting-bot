import os
import random
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
API_KEY = os.getenv("ODDSAPI_KEY")

# -----------------------------
# Calcul des mises et gains
# -----------------------------
def calculate_bets(c1, c2):
    mise1 = round(random.uniform(5, 10), 2)
    mise2 = round((mise1 * c1) / c2, 2) if c2 else 0
    gain1 = round(mise1 * c1 - mise1 - mise2, 2)
    gain2 = round(mise2 * c2 - mise1 - mise2, 2)
    return mise1, mise2, gain1, gain2

# -----------------------------
# Liste des championnats actifs
# -----------------------------
def list_championnats():
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        sports = r.json()
        return {s['key']: s['title'] for s in sports if s['active']}
    except Exception as e:
        print("Erreur récupération sports:", e)
        return {}

# -----------------------------
# Récupère un seul match d’un championnat
# -----------------------------
def get_one_match(championnat):
    url = f"https://api.the-odds-api.com/v4/sports/{championnat}/odds/?apiKey={API_KEY}&regions=eu&markets=1x2&oddsFormat=decimal"
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
                return teams, c1, c2, start_time, link
        return None
    except Exception as e:
        print("Erreur JSON :", e)
        return None

# -----------------------------
# Commande /scan
# -----------------------------
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Championnat passé en argument ou par défaut
    championnat_dispo = list_championnats()
    if context.args:
        key = context.args[0]
        if key not in championnat_dispo:
            await update.message.reply_text(f"Championnat invalide !\nVoici les actifs : {', '.join(championnat_dispo.keys())}")
            return
        cle_championnat = key
    else:
        # premier actif par défaut
        cle_championnat = list(championnat_dispo.keys())[0] if championnat_dispo else None

    if not cle_championnat:
        await update.message.reply_text("Aucun championnat actif trouvé.")
        return

    match = get_one_match(cle_championnat)
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

# -----------------------------
# Lancement du bot
# -----------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("scan", scan))
    print("Bot démarré… envoie /scan [championnat] pour recevoir un match")
    app.run_polling()
