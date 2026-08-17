import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from groq import Groq

# Pega as chaves não importa o nome que você usou
BOT_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TOKEN") or os.getenv("TELEGRAM_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ") or os.getenv("GROQ_API_KEY_GROQ") or os.getenv("GROQ_")

# Acha automatico se o nome for GROQ_API_KEY ou GROQ_TOKEN etc
if not GROQ_KEY:
    for k,v in os.environ.items():
        if "GROQ" in k.upper():
            GROQ_KEY = v
            break

client = Groq(api_key=GROQ_KEY)

GRUPO_PROMPT = """
Você é a vendedora oficial da Systeme.io Brasil. Foco: VENDER.

Systeme.io = tudo-em-um que substitui ClickFunnels + Mailchimp + Hotmart. Faz funil, email ilimitado, curso online, afiliados, blog.

REGRAS FIXAS:
- SEMPRE português do Brasil, nunca outro idioma
- MÁXIMO 5 linhas curtas com emoji
- Sempre termina com link: https://systeme.io/pt?sa=sa0279228743abe942e022d749c9984a272aad2f09
- Se falarem outro assunto, volta pra Systeme.io
"""

PRIVADO_PROMPT = """
Você é assistente útil e direta.
REGRAS:
- SEMPRE português do Brasil
- Máximo 8 linhas, sem textão
- Se for sobre Systeme.io use: https://systeme.io/pt?sa=sa0279228743abe942e022d749c9984a272aad2f09
"""

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    if not texto: return
    chat_type = update.effective_chat.type

    if chat_type in ['group','supergroup']:
        if f"@{context.bot.username}" not in texto and not update.message.reply_to_message:
            return
        system = GRUPO_PROMPT
    else:
        system = PRIVADO_PROMPT

    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":system},{"role":"user","content":texto}],
            max_tokens=200,
            temperature=0.6
        )
        await update.message.reply_text(resp.choices[0].message.content)
    except Exception as e:
        print(f"Erro Groq: {e}")

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()
