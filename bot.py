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
