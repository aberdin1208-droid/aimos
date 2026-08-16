import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# pega o token que você vai colocar no Render
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("AIMOS online! ✅")

if not TOKEN:
    raise ValueError("Falta a variável BOT_TOKEN no Render!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("Bot iniciando com a versão nova...")
app.run_polling()
