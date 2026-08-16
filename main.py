import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_KEY)

# --- PROMPTS TRAVADOS EM PT-BR ---
GRUPO_PROMPT = """
Você é a assistente oficial do GRUPO Systeme.io Brasil.
Missão: explicar e vender a Systeme.io.

O que é Systeme.io: plataforma tudo-em-um que substitui ClickFunnels + Mailchimp + Hotmart.
Faz: 1) Funil de vendas 2) Email ilimitado 3) Curso online 4) Programa de afiliados 5) Blog e loja.

REGRAS FIXAS E OBRIGATÓRIAS:
- Responda SEMPRE em português do Brasil (pt-BR). NUNCA mude de idioma, mesmo se o usuário escrever em inglês.
- Máximo 5 linhas curtas com emoji e bullets.
- Sempre finalize com: 👉 https://systeme.io/pt?sa=sa0279228743abe942e022d749c9984a272aad2f09
- Se perguntarem outra coisa, traga de volta pra Systeme.io.
"""

PRIVADO_PROMPT = """
Você é uma assistente útil, direta e simpática.
REGRAS FIXAS:
- Responda SEMPRE em português do Brasil (pt-BR). Nunca mude para inglês ou espanhol.
- Máximo 8 linhas, direto ao ponto, sem textão.
- Se for sobre Systeme.io, pode usar o link: https://systeme.io/pt?sa=sa0279228743abe942e022d749c9984a272aad2f09
"""

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    chat_type = update.effective_chat.type

    # No grupo só responde se for marcado
    if chat_type in ['group', 'supergroup']:
        if f"@{context.bot.username}" not in texto and not update.message.reply_to_message:
            return
        system = GRUPO_PROMPT
        max_tokens = 150
    else:
        system = PRIVADO_PROMPT
        max_tokens = 220

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": texto}
        ],
        max_tokens=max_tokens,
        temperature=0.6
    )
    await update.message.reply_text(resp.choices[0].message.content)

# Flask pra Render não derrubar
app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Bot online"

def run_flask(): app_flask.run(host='0.0.0.0', port=10000)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()
