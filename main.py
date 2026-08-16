import os
import threading
from flask import Flask
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from groq import Groq

TOKEN = os.getenv("TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

flask_app = Flask(__name__)
@flask_app.route("/")
def home():
    return "Bot online!"

async def start(update, context):
    await update.message.reply_text("Finalmente online!")

async def responde(update, context):
    try:
        client = Groq(api_key=GROQ_KEY)
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": update.message.text}]
        )
        await update.message.reply_text(completion.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Erro Groq: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responde))
    app.run_polling()

if __name__ == "__main__":
    threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    main()
