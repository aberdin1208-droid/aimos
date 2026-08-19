import os
import asyncio
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
def home():
    return "aberdin_IA online"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

def limitar(texto, max_l=4):
    linhas = [l for l in texto.split('\n') if l.strip()!='']
    return '\n'.join(linhas[:max_l])

def get_botoes():
    keyboard = [
        [InlineKeyboardButton("💎 Systeme.io - O que é?", callback_data="oquee")],
        [InlineKeyboardButton("💰 Planos e Preços", callback_data="planos")],
        [InlineKeyboardButton("🎓 Afiliados 60% Vitalício", callback_data="afiliados")],
        [InlineKeyboardButton("🚀 Começar GRÁTIS Agora", url=LINK)]
    ]
    return InlineKeyboardMarkup(keyboard)

# CORRIGIDO: Agora não trava o bot
async def get_groq(sistema, usuario):
    def _call():
        return client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":sistema},{"role":"user","content":usuario}],
            temperature=0.6,
            max_tokens=200
        )
    r = await asyncio.to_thread(_call)
    return r.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🤖 Sou a IA da Systeme.io\n🚀 Funil + Email + Curso + Afiliados\n📧 2000 contatos grátis\n👇\n{LINK}",
        reply_markup=get_botoes(),
        disable_web_page_preview=True
    )

async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for m in update.message.new_chat_members:
        if m.is_bot:
            continue
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🤖 Bem-vindo {m.first_name}!\n🚀 Systeme.io tudo em 1\n📧 Email ilimitado 2k grátis\n👇 {LINK}",
            reply_markup=get_botoes(),
            disable_web_page_preview=True
        )

async def botoes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == "oquee":
        texto = (
            f"💎 O que é a Systeme.io? É tudo-em-um de verdade:\n\n"
            f"🚀 1. FUNIL: Cria página de captura, vendas e checkout igual ClickFunnels\n"
            f"📧 2. EMAIL ILIMITADO: 2.000 contatos grátis e envios ilimitados\n"
            f"🎓 3. CURSOS: Hospeda seu curso sem pagar 10% por venda igual Hotmart\n"
            f"🤝 4. AFILIADOS: Cria seu programa e paga 60% no automático\n"
            f"💰 Substitui 4 ferramentas caras por $27/mês. 500 mil já usam.\n\n"
            f"👇 Cria sua conta grátis aqui:\n{LINK}"
        )
    elif query.data == "planos":
        texto = f"💰 Grátis: 2000 contatos\n🚀 Pago desde $27/mês\n👇 {LINK}"
    else:
        texto = f"🎓 Afiliado 60% vitalício\n🚀 Vende tudo junto\n👇 {LINK}"

    await context.bot.send_message(chat_id=chat_id, text=texto, reply_markup=get_botoes(), disable_web_page_preview=True)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if not txt:
        return
    sistema = f"Voce e Aberdin IA, vendedora Systeme.io. SEJA CURTA: max 3 linhas, PT-BR, emoji, sempre CTA + LINK {LINK}. Fale que e IA."
    try:
        resp = await get_groq(sistema, txt)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=limitar(resp),
            reply_markup=get_botoes(),
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(f"Erro Groq: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"🤖 Systeme.io tudo em 1\n📧 2k grátis\n👇 {LINK}",
            reply_markup=get_botoes(),
            disable_web_page_preview=True
        )

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

    # CORRIGIDO: Não acumula mensagem e fica 24h sem travar
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
