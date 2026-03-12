import os
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔹 Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # token Telegram
ODDS_API_KEY = "2b2ca3fe2db06657aaeaefb313884a31639e9854191069304c40f3f8171a52fc"  # ta clé Odds API

HEADERS = {
    "User-Agent": "TelegramBot"
}

# 🔹 Récupère les matchs à venir
def get_matches():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?regions=eu&markets=h2h&apiKey={ODDS_API_KEY}"
    r = requests.get(url, headers=HEADERS)
    data = r.json()
    return data

# 🔹 Commande /scan
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        matches = get_matches()
        if not matches:
            await update.message.reply_text("Aucun match trouvé pour le moment.")
            return

        # 🔹 Choisir un match aléatoire
        match = random.choice(matches)
        home = match["home_team"]
        away = match["away_team"]
        commence_time = match["commence_time"]

        # 🔹 Vérifier les bookmakers
        bookmakers = match.get("bookmakers", [])
        if not bookmakers:
            await update.message.reply_text(f"Match trouvé : {home} vs {away}\n⏰ {commence_time}\nMais pas de cotes disponibles.")
            return

        # 🔹 Prendre le premier bookmaker et les cotes H2H
        outcomes = bookmakers[0]["markets"][0]["outcomes"]
        home_price = float(outcomes[0]["price"])
        away_price = float(outcomes[1]["price"])

        # 🔹 Calcul mise pour gain cible ±2€
        gain_target = random.uniform(1.8, 2.2)
        stake_home = round(gain_target / home_price, 2)
        stake_away = round(gain_target / away_price, 2)

        # 🔹 Limiter la mise entre 5 et 10€
        stake_home = min(max(stake_home, 5), 10)
        stake_away = min(max(stake_away, 5), 10)

        msg = f"⚽ Match : {home} vs {away}\n"
        msg += f"⏰ Heure : {commence_time}\n"
        msg += f"💰 Cotes ({bookmakers[0]['title']}): {home}={home_price}, {away}={away_price}\n"
        msg += f"💵 Mise pour gain ±2€ : {home}={stake_home}€, {away}={stake_away}€"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"Erreur lors du scan : {e}")

# 🔹 Création et lancement du bot
app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("scan", scan))
app.run_polling()
