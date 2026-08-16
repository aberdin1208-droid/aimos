import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    texto = update.message.text

    # No grupo só responde se marcar o bot ou usar /ask
    if update.message.chat.type!= "private":
        if f"@{context.bot.username}" not in texto and not texto.startswith("/ask"):
            return

    pergunta = texto.replace("/ask", "").replace(f"@{context.bot.username}", "").strip()
    if not pergunta:
        return

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": pergunta}]
    )

    await update.message.reply_text(resp.choices[0].message.content)

app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("ask", responder))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
app.run_polling()
