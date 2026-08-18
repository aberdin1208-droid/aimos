import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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

def limitar(texto, max_l=4):
    linhas = [l for l in texto.split('\n') if l.strip()!='']
    return '\n'.join(linhas[:max_l])

def get_botoes():
    keyboard = [
        [InlineKeyboardButton("🚀 O que é?", callback_data="oquee")],
        [InlineKeyboardButton("💰 Preços", callback_data="planos")],
        [InlineKeyboardButton("🎓 Afiliados", callback_data="afiliados")],
        [InlineKeyboardButton("👉 Começar GRÁTIS", url=LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_groq(sistema, usuario):
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"system","content":sistema},{"role":"user","content":usuario}],
        temperature=0.6, max_tokens=200
    )
    return r.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🤖 Sou a IA da Systeme.io\n🚀 Funil + Email + Curso + Afiliados\n📧 2000 contatos grátis\n👇\n{LINK}", reply_markup=get_botoes(), disable_web_page_preview=True)

async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for m in update.message.new_chat_members:
        if m.is_bot: continue
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🤖 Bem-vindo {m.first_name}!\n🚀 Systeme.io tudo em 1\n📧 Email ilimitado 2k grátis\n👇 {LINK}", reply_markup=get_botoes(), disable_web_page_preview=True)

async def botoes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "oquee":
        # SÓ ESSE FICA LONGO EXPLICATIVO
        texto = (
            f"🤖 Systeme.io é tudo-em-um pra vender online\n\n"
            f"🚀 O que faz: Funil + Email ILIMITADO (2k grátis) + Curso + Afiliados + Blog\n"
            f"💰 Substitui ClickFunnels + Mailchimp + Hotmart por $27/mês\n"
            f"🎓 500 mil empreendedores já usam\n\n"
            f"👇 Cria sua conta grátis:\n{LINK}"
        )
