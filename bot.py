import os
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")


def find_match():

    matches = [
        ("PSG vs Lyon", "21:00", 2.02, 1.63, "https://megapari.com/football/123"),
        ("Chelsea vs Arsenal", "18:30", 1.95, 1.70, "https://megapari.com/football/456"),
        ("Barcelona vs Sevilla", "20:45", 2.10, 1.60, "https://megapari.com/football/789"),
        ("Milan vs Napoli", "19:30", 2.05, 1.66, "https://megapari.com/football/321"),
    ]

    for m in matches:

        name = m[0]
        time = m[1]
        cote1 = m[2]
        cotex2 = m[3]
        link = m[4]

        if 1.9 <= cote1 <= 2.2 and 1.55 <= cotex2 <= 1.75:
            return name, time, cote1, cotex2, link

    return None


def calculate_bets(c1, c2):

    mise1 = round(random.uniform(5, 10), 2)

    mise2 = round((mise1 * c1) / c2, 2)

    gain1 = round(mise1 * c1 - mise1 - mise2, 2)
    gain2 = round(mise2 * c2 - mise1 - mise2, 2)

    return mise1, mise2, gain1, gain2


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = (
        "Bot actif ✅\n\n"
        "Commande disponible :\n"
        "/scan → chercher un match avec les cotes"
    )

    await update.message.reply_text(message)


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Scan des matchs... ⏳")

    result = find_match()

    if not result:
        await update.message.reply_text("Aucun match valide trouvé.")
        return

    match, time, c1, c2, link = result

    mise1, mise2, gain1, gain2 = calculate_bets(c1, c2)

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

Lien du match :
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
