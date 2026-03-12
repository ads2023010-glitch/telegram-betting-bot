import os
import time
import random

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


TOKEN = os.getenv("TOKEN")


def get_matches():

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get("https://megapari.com/sport/football")

    time.sleep(6)

    matches = []

    try:

        events = driver.find_elements(By.CSS_SELECTOR, ".event")

        for e in events[:20]:

            try:
                name = e.text.split("\n")[0]

                # valeurs de test (à remplacer par les vraies cotes)
                cote1 = round(random.uniform(1.9, 2.2), 2)
                cotex2 = round(random.uniform(1.55, 1.75), 2)

                time_match = "20:00"

                link = "https://megapari.com"

                matches.append((name, time_match, cote1, cotex2, link))

            except:
                pass

    except:
        pass

    driver.quit()

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

    await update.message.reply_text("Scan des matchs... ⏳")

    result = find_match()

    if not result:

        await update.message.reply_text("Aucun match trouvé.")
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
