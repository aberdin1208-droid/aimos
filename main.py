import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# log pra você ver no Render
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot online! Aberdin aqui.")

def main():
    if not TOKEN:
        print("ERRO: Variável TOKEN não encontrada no Render")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    # CORREÇÃO DO SEU ERRO: não pode encadear tudo
    app.add_handler(CommandHandler("start", start))
    
    print("Bot iniciando...")
    app.run_polling()

if __name__ == "__main__":
    main()
