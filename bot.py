import os
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 🔹 Variables d'environnement
API_KEY = os.getenv("ODDSAPI_KEY")       # clé TheOddsAPI
TOKEN = os.getenv("TELEGRAM_TOKEN")      # token Telegram

ODDS_URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=eu&markets=h2h&apiKey={API_KEY}"

# 🔹 Fonction scan
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(ODDS_URL)
        matches = r.json()

        if not matches:
            await update.message.reply_text("Aucun match trouvé pour le moment.")
            return

        # 🔹 Choisir un match aléatoire
        match = random.choice(matches)
        home = match['home_team']
        away = match['away_team']
        time = match['commence_time']

        # 🔹 Première cote disponible pour chaque équipe
        bookmaker = match['bookmakers'][0]
        outcomes = bookmaker['markets'][0]['outcomes']
        home_price = outcomes[0]['price']
        away_price = outcomes[1]['price']

        # 🔹 Calcul mise pour gain aléatoire mais mise comprise entre 5 et 10€
        gain_target = random.uniform(5, 10)   # gain cible entre 5 et 10 €
        stake_home = round(gain_target / home_price, 2)
        stake_away = round(gain_target / away_price, 2)

        # 🔹 S'assurer que la mise reste entre 5 et 10€
        stake_home = min(max(stake_home, 5), 10)
        stake_away = min(max(stake_away, 5), 10)

        # 🔹 Message à envoyer
        msg = f"🏀 Match : {home} vs {away}\n"
        msg += f"⏰ Heure : {time}\n"
        msg += f"💰 Cotes ({bookmaker['title']}): {home}={home_price}, {away}={away_price}\n"
        msg += f"💵 Mise recommandée (5-10€) : {home}={stake_home}€, {away}={stake_away}€"

        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"Erreur lors du scan : {e}")

# 🔹 Création du bot
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("scan", scan))

# 🔹 Lancement du bot
app.run_polling()
