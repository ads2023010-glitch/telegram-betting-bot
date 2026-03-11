import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")


def get_matches():

    url = "https://megapari.com"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    matches = []

    for m in soup.find_all("div"):

        text = m.get_text(strip=True)

        if "vs" in text.lower():
            matches.append(text)

        if len(matches) >= 5:
            break

    return matches


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Bot actif.\nUtilise la commande /scan pour chercher des matchs."
    )


async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("Scan des matchs en cours...")

    matches = get_matches()

    if not matches:
        await update.message.reply_text("Aucun match trouvé.")
        return

    message = "Matchs trouvés :\n\n"

    for m in matches:
        message += f"{m}\n"

    await update.message.reply_text(message)


def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("Bot démarré")

    app.run_polling()


if __name__ == "__main__":
    main()
