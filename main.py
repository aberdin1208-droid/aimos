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
        messages=[
            {"role":"system","content":sistema},
            {"role":"user","content":usuario}
        ],
        temperature=0.6,
        max_tokens=200
    )
    return r.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🤖 Sou a IA da Systeme.io\n🚀 Funil + Email + Curso + Afiliados\n📧 2000 contatos grátis\n👇\n{LINK}", reply_markup=get_botoes())

async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for m in update.message.new_chat_members:
        if m.is_bot: continue
        await update.message.reply_text(f"🤖 Bem-vindo {m.first_name}!\n🚀 Systeme.io tudo em 1\n📧 Email ilimitado 2k grátis\n👇 {LINK}", reply_markup=get_botoes())

async def botoes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "oquee":
        await query.message.reply_text(f"🤖 Systeme.io = tudo em 1\n🚀 Funil + Email + Curso\n📧 2k contatos grátis\n👇 {LINK}", reply_markup=get_botoes())
    elif query.data == "planos":
        await query.message.reply_text(f"💰 Grátis: 2000 contatos\n🚀 Pago desde $27/mês\n👇 {LINK}", reply_markup=get_botoes())
    elif query.data == "afiliados":
        await query.message.reply_text(f"🎓 Afiliado 60% vitalício\n🚀 Vende tudo junto\n👇 {LINK}", reply_markup=get_botoes())

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if not txt: return
    sistema = f"Voce e Aberdin IA, vendedora Systeme.io. SEJA CURTA: max 3 linhas, PT-BR, emoji, sempre CTA + LINK {LINK}. Fale que e IA."
    try:
        resp = await get_groq(sistema, txt)
        await update.message.reply_text(limitar(resp), reply_markup=get_botoes())
    except Exception as e:
        logging.error(f"Erro Groq: {e}")
        await update.message.reply_text(f"🤖 Systeme.io tudo em 1\n📧 2k grátis\n👇 {LINK}", reply_markup=get_botoes())

def main():
    if not BOT_TOKEN or not GROQ_API_KEY:
        logging.error("Falta BOT_TOKEN ou GROQ_API_KEY")
        return
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botoes_callback))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, boas_vindas))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()

if __name__ == '__main__':
    main()
