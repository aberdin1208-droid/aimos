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
LINK_SYSTEME = "https://systeme.io/pt?sa=sa0279228743abe942e022d749c9984a272aad2f09"

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "aberdin_IA bot online"

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

def limitar_linhas(texto, max_linhas):
    linhas = [l for l in texto.strip().split('\n') if l.strip()!= '']
    return '\n'.join(linhas[:max_linhas])

async def get_groq(sistema, usuario):
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":sistema},{"role":"user","content":usuario}],
        temperature=0.7,
        max_tokens=400
    )
    return r.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot do aberdin_IA online! 🚀 Me marca aqui no grupo.")

async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # só no grupo
    if update.effective_chat.type == 'private':
        return
    for m in update.message.new_chat_members:
        if m.is_bot:
            continue
        msg = f"""Bem-vindo {m.first_name} ao {update.effective_chat.title}! 🚀
Grupo sobre Systeme.io e como vender
📧 Email ilimitado + funil que vende
🎓 Curso e afiliados juntos
500 mil usam, grátis pra testar 👇
{LINK_SYSTEME}"""
        await update.message.reply_text(limitar_linhas(msg, 5))

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    texto_user = update.message.text
    is_private = chat.type == 'private'
    max_linhas = 8 if is_private else 5

    try:
        qtd = await context.bot.get_chat_member_count(chat.id)
        info_grupo = f"Você está no grupo '{chat.title}' ({qtd} membros). Link: https://t.me/aberdin_IA. Este grupo é sobre a Systeme.io e explicações com intuito de venda. Objetivo é ensinar e converter."
    except:
        info_grupo = "Grupo https://t.me/aberdin_IA sobre Systeme.io com intuito de venda."

    sistema = f"""
{info_grupo}
Você é vendedora oficial da Systeme.io no Brasil.

O QUE É: Tudo-em-um que substitui ClickFunnels + Mailchimp + Hotmart. Funil completo com checkout e upsell, Email ILIMITADO com automação, criar e vender curso, programa de afiliados próprio, blog e loja. Grátis até 2.000 contatos sem cartão.

REGRAS:
- Sempre PT-BR, max {max_linhas} linhas, bullets com 🚀 📧 🎓
- Estrutura: 1 linha resolve + 2 bullets + "500 mil empreendedores usam" + CTA + LINK
- Link obrigatório: {LINK_SYSTEME}
- Se "é caro?": É grátis pra começar, plano mais barato do Brasil
- Se "é difícil?": 3 cliques, já vem template pronto
- Se "já tenho ferramenta?": Systeme.io junta tudo que você paga separado num lugar só
"""

    try:
        resp = await get_groq(sistema, texto_user)
        await update.message.reply_text(limitar_linhas(resp, max_linhas))
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
