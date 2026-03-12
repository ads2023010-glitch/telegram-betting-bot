import os
import requests
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

API_URL = "https://4689732mp.pro/service-api/LiveFeed/Get1x2_VZip?count=200&lng=fr&gr=824&mode=4&country=6&partner=192&virtualSports=true&countryFirst=true&noFilterBlockEvent=true"


def get_matches():

    r = requests.get(API_URL)

    data = r.json()

    matches = []

    for league in data.get("Value", []):

        for match in league.get("E", []):

            try:

                team1 = match["O1"]
                team2 = match["O2"]

                name = f"{team1} vs {team2}"

                cote1 = float(match["C"][0][0])
                cote2 = float(match["C"][0][2])

                time_match = match["S"]

                link = "https://megapari.com"

                matches.append((name, time_match, cote1, cote2, link))

            except:
                pass

    return matches


def find_match():

    matches = get_matches()

    for m in matches:

        name, time_match, c1, c2, link = m

        if 1.9 <= c1 <= 2.2 and 1.55 <= c2 <= 1.75:

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

    await update.message.reply_text("Analyse des matchs... ⏳")

    result = find_match()

    if not result:

        await update.message.reply_text("Aucun match correspondant trouvé.")
        return

    match, time_match, c1, c2, link = result

    mise1, mise2, gain1, gain2 = calculate_bets(c1, c2)

    message = f"""
Match trouvé ⚽

{match}
Heure : {time_match}

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
