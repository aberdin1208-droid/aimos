import os
import logging
import threading
import json
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PORT = int(os.getenv("PORT", 10000))
LINK_SYSTEME = "https://systeme.io/pt?sa=sa0279228743abe942e022d749c9984a272aad2f09"

logging.basicConfig(level=logging.INFO)

# tenta groq, se não tiver usa requests (pra não dar Failed)
try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY)
    USE_GROQ_LIB = True
except:
    USE_GROQ_LIB = False
    try:
        import requests
    except:
        requests = None

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "aberdin_IA online"
def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

def limitar_linhas(texto, max_linhas):
    linhas = [l for l in texto.strip().split('\n') if l.strip()!='']
    return '\n'.join(linhas[:max_linhas])

async def get_groq(sistema, usuario):
    usuario_pt = f"{usuario}\n\n[INSTRUÇÃO FINAL OBRIGATÓRIA: Responda SEMPRE em português do Brasil, NUNCA em inglês. Se responder em inglês você falhou.]"
    if USE_GROQ_LIB:
        r = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":sistema},{"role":"user","content":usuario_pt}],
            temperature=0.6,
            max_tokens=400
        )
        return r.choices[0].message.content
    else:
        # fallback sem lib groq, usando API direta
        import urllib.request
        url = "https://api.groq.com/openai/v1/chat/completions"
        data = json.dumps({
            "model":"llama-3.1-8b-instant",
            "messages":[{"role":"system","content":sistema},{"role":"user","content":usuario_pt}],
            "temperature":0.6,
            "max_tokens":400
        }).encode()
        req = urllib.request.Request(url, data=data, headers={"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"})
        with urllib.request.urlopen(req) as resp:
            j = json.loads(resp.read().decode())
            return j["choices"][0]["message"]["content"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot do aberdin_IA online! 🚀")

async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private':
        return
    for m in update.message.new_chat_members:
        if m.is_bot: continue
        msg = f"""Bem-vindo {m.first_name} ao {update.effective_chat.title}! 🚀
Grupo https://t.me/aberdin_IA sobre Systeme.io
📧 Email ilimitado + funil que vende
🎓 Curso e afiliados no mesmo lugar
500 mil usam, grátis pra testar 👇
{LINK_SYSTEME}"""
        await update.message.reply_text(limitar_linhas(msg, 5))

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    texto = update.message.text
    is_private = chat.type == 'private'
    max_linhas = 8 if is_private else 5

    try:
        qtd = await context.bot.get_chat_member_count(chat.id)
        info_grupo = f"Você está no grupo '{chat.title}' ({qtd} membros) https://t.me/aberdin_IA. Grupo sobre Systeme.io e explicações com intuito de venda."
    except:
        info_grupo = "Grupo https://t.me/aberdin_IA sobre Systeme.io e explicações com intuito de venda."

    sistema = f"""
{info_grupo}
IDIOMA OBRIGATÓRIO: PORTUGUÊS DO BRASIL. É PROIBIDO RESPONDER EM INGLÊS. NUNCA USE INGLÊS, SEMPRE PT-BR.

Você é vendedora oficial da Systeme.io no Brasil.
O QUE É: Tudo-em-um que substitui ClickFunnels + Mailchimp + Hotmart. Funil com checkout e upsell, Email ILIMITADO, criar e vender curso, programa de afiliados, blog e loja. Grátis até 2.000 contatos.

REGRAS:
- Sempre PT-BR, max {max_linhas} linhas, bullets 🚀 📧 🎓
- Estrutura: 1 linha resolve + 2 bullets + "500 mil empreendedores usam" + CTA + LINK
- Link obrigatório: {LINK_SYSTEME}
- Se "é caro?": É grátis pra começar, plano mais barato do Brasil
- Se "é difícil?": 3 cliques, já vem template pronto
"""

    try:
        resp = await get_groq(sistema, texto)
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
