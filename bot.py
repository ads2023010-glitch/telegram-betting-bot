import os
import requests
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

API_URL = "https://mp267893.pro/fatman-api/a6f69e4388362d761ee5bb073edb23ae3d9341fb/event.json"


def get_matches():

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        r = requests.get(API_URL, headers=headers, timeout=10)
        data = r.json()
    except:
        return []

    matches = []

    events = data.get("events", [])

    for event in events:

        team1 = event.get("team1", "")
        team2 = event.get("team2", "")

        name = f"{team1} vs {team2}"

        time = event.get("startTime", "??")

        # ces clés peuvent varier selon l'API
        cote1 = event.get("odd1", 0)
        cotex2 = event.get("oddX2", 0)

        link = "https://megapari.com"

        matches.append((name, time, cote1, cotex2, link))

    return matches


def find_match():

    matches = get_matches()

    for m in matches:

        name, time, c1, c2, link = m

        if 1.9 <= float(c1) <= 2.2 and 1.55 <= float(c2) <= 1.75:
            return m

    return None


def calculate_bets(c1, c2):

    mise1 = round(random.uniform(5, 10), 2)

    mise2 = round((mise1 * c1) / c2, 2)

    gain1 = round(mise1 * c1 - mise1 - mise2, 2)
    gain2 = round(mise2 * c2 - mise1 - mise2, 2)

    return mise1, mise2, gain1, gain2


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Bot actif ✅\n\nCommande disponible : /scan"
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Scan des matchs... ⏳")

    result = find_match()

    if not result:
        await update.message.reply_text("Aucun match correspondant trouvé.")
        return

    match, time, c1, c2, link = result

    mise1, mise2, gain1, gain2 = calculate_bets(float(c1), float(c2))

    message = f"""
Match trouvé ⚽

{match}
Heure : {time}

Cote 1 : {c1}
Cote X2 : {c2}

Mise 1 : {mise1} €
Mise X2 : {mise2} €

Gain si 1 gagne : {gain1} €
Gain si X2 gagne : {gain2} €

Lien :
{link}
"""

    await update.message.reply_text(message)


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("Bot démarré")

    app.run_polling()


if __name__ == "__main__":
    main()
