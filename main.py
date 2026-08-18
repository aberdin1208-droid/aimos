import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 10000))
LINK = "https://systeme.io/pt?sa=sa0279228743abe942e022d749c9984a272aad2f09"

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "aberdin_IA online"
def run_flask(): flask_app.run(host="0.0.0.0", port=PORT)

def limitar(texto, max_l=5):
    linhas = [l for l in texto.split('\n') if l.strip()!='']
    return '\n'.join(linhas[:max_l])

async def get_groq(sistema, usuario):
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":sistema},
            {"role":"user","content":usuario}
        ],
        temperature=0.6,
        max_tokens=350
    )
    return r.choices[0].message.content

async def start(update, context):
    await update.message.reply_text("Sou a IA da Systeme.io 🤖 me pergunta!")

async def boas_vindas(update, context):
    for m in update.message.new_chat_members:
        if m.is_bot: continue
        await update.message.reply_text(f"Sou uma IA 🤖 Bem-vindo {m.first_name}!\n🚀 Funil 3 cliques\n📧 Email ilimitado 2k gratis\n🎓 Curso + afiliados\n500 mil usam 👇\n{LINK}")

async def responder(update, context):
    txt = update.message.text
    if not txt: return
    sistema = f"""Voce e a Aberdin IA, vendedora oficial Systeme.io. Fale que e IA.
O QUE E: tudo-em-um ClickFunnels + Mailchimp + Hotmart. Funil checkout upsell, email ILIMITADO 2000 gratis, curso, afiliados, blog.
REGRAS: Sempre PT-BR, max 5 linhas, topicos com emoji 🚀 📧 🎓, estrutura: Sou uma IA + 2 bullets + 500 mil usam + CTA + LINK {LINK}"""
    try:
        resp = await get_groq(sistema, txt)
        await update.message.reply_text(limitar(resp))
    except Exception as e:
        logging.error(e)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, boas_vindas))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()

if __name__ == '__main__':
    main()
