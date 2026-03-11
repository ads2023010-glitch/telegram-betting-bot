import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Scan des matchs en cours...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot actif. Utilise /scan")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))

    print("Bot démarré")
    app.run_polling()

if __name__ == "__main__":
    main()
async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cote1 = 2.0
    cote2 = 1.65

    mise1 = 7
    mise2 = round((mise1 * cote1) / cote2, 2)

    gain_si_1 = round(mise1 * cote1 - mise1 - mise2, 2)
    gain_si_x2 = round(mise2 * cote2 - mise1 - mise2, 2)

    message = f"""
Match trouvé ⚽

Cote 1 : {cote1}
Cote X2 : {cote2}

Mise 1 : {mise1}€
Mise X2 : {mise2}€

Gain si 1 gagne : {gain_si_1}€
Gain si X2 gagne : {gain_si_x2}€
"""

    await update.message.reply_text(message)
