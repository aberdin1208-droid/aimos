import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TOKEN")

app = Flask(__name__)
@web.route('/')
def home():
    return "Bot Aimos online!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot online 100% free!")

def main():
    if not TOKEN:
        print("ERRO: TOKEN nao encontrado")
        return
    threading.Thread(target=run_flask, daemon=True).start()
    bot = ApplicationBuilder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.run_polling()

if __name__ == "__main__":
    main()
