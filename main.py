import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("AIMOS online 😈 manda a pergunta")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = update.message.text
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é o AIMOS, sarcástico, inteligente e debochado. Responda curto."},
                {"role": "user", "content": pergunta}
            ]
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        await update.message.reply_text(f"Deu erro: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
