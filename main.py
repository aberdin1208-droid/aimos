import os, threading, logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
print(f"TOKEN encontrado: {bool(TOKEN)}")

web = Flask(__name__)
@web.route("/")
def home():
    return "AIMOS online!", 200

def run_web():
    web.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("AIMOS online! ✅")

def run_bot():
    if not TOKEN:
        print("ERRO: BOT_TOKEN nao configurado!")
        return
    print("Iniciando bot AIMOS...")
    ApplicationBuilder().token(TOKEN).build().add_handler(CommandHandler("start", start)).run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    run_bot()
