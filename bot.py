import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

API_KEY = os.getenv("ODDSAPI_KEY")
ODDS_URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=eu&markets=h2h&apiKey={API_KEY}"

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(ODDS_URL)
        matches = r.json()
        if not matches:
            await update.message.reply_text("Aucun match trouvé pour le moment.")
            return

        # Prendre seulement le premier match
        match = matches[0]
        home = match['home_team']
        away = match['away_team']
        time = match['commence_time']

        # Récupérer la première cote disponible pour chaque équipe
        bookmaker = match['bookmakers'][0]
        outcomes = bookmaker['markets'][0]['outcomes']
        home_price = outcomes[0]['price']
        away_price = outcomes[1]['price']

        # Calcul de mise pour ~2€ de gain
        stake_home = round(2 / home_price, 2)
        stake_away = round(2 / away_price, 2)

        msg = f"🏀 Match : {home} vs {away}\n"
        msg += f"⏰ Heure : {time}\n"
        msg += f"💰 Cotes ({bookmaker['title']}): {home}={home_price}, {away}={away_price}\n"
        msg += f"💵 Mise approximative pour ~2€ de gain : {home}={stake_home}€, {away}={stake_away}€\n"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"Erreur lors du scan : {e}")

# Création du bot
TOKEN = os.getenv("TELEGRAM_TOKEN")
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("scan", scan))

app.run_polling()
