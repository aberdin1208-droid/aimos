import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "OK - Bot Aimos online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Finalmente online!")

def main():
    if not TOKEN:
        print("ERRO: TOKEN nao encontrado")
        return
    threading.Thread(target=run_flask, daemon=True).start()
    print("Bot iniciando...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
