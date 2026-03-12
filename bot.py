import os
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔹 Variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # token Telegram
API_KEY = "03bb4a0590396c4695f93a8eac3ecf23" # clé API-SPORTS

HEADERS = {
    "x-apisports-key": API_KEY
}

# 🔹 Fonction pour récupérer les matchs
def get_matches():
    url = "https://v3.football.api-sports.io/fixtures?status=NS&league=39&season=2025"  # Premier League
    r = requests.get(url, headers=HEADERS)
    data = r.json()
    return data.get("response", [])

# 🔹 Commande /scan
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        matches = get_matches()
        if not matches:
            await update.message.reply_text("Aucun match trouvé pour le moment.")
            return

        # 🔹 Choisir un match aléatoire
        match = random.choice(matches)
        fixture = match["fixture"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        time = fixture["date"]

        # 🔹 Vérifier si les bookmakers existent
        bookmakers = match.get("bookmakers", [])
        if not bookmakers:
            await update.message.reply_text(f"Match trouvé : {home} vs {away}\n⏰ {time}\nMais pas de cotes disponibles.")
            return

        # 🔹 Prendre le premier bookmaker
        outcomes = bookmakers[0]["bets"][0]["values"]
        home_price = float(outcomes[0]["odd"])
        away_price = float(outcomes[1]["odd"])

        # 🔹 Calcul mise pour gain cible ±2 €
        gain_target = random.uniform(1.8, 2.2)  # gain ciblé entre 1.8 et 2.2 €
        stake_home = round(gain_target / home_price, 2)
        stake_away = round(gain_target / away_price, 2)

        # 🔹 S'assurer que la mise est entre 5 et 10 €
        stake_home = min(max(stake_home, 5), 10)
        stake_away = min(max(stake_away, 5), 10)

        msg = f"⚽ Match : {home} vs {away}\n"
        msg += f"⏰ Heure : {time}\n"
        msg += f"💰 Cotes ({bookmakers[0]['name']}): {home}={home_price}, {away}={away_price}\n"
        msg += f"💵 Mise pour gain ±2€ : {home}={stake_home}€, {away}={stake_away}€"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"Erreur lors du scan : {e}")

# 🔹 Création et lancement du bot
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("scan", scan))
app.run_polling()
