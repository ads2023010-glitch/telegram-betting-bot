from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TOKEN")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Scan en cours...")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("scan", scan))

app.run_polling()