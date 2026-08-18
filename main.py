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

try:
    from groq import Groq
    groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
    USE_GROQ_LIB = bool(groq_client)
except:
    USE_GROQ_LIB = False
    groq_client = None

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "aberdin_IA online"
def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

def limitar_linhas(texto, max_linhas=5):
    linhas = [l for l in texto.strip().split('\n') if l.strip()!='']
    return '\n'.join(linhas[:max_linhas])

async def get_groq(sistema, usuario):
    prompt = f"{usuario}\n\n[RESPONDA SEMPRE EM PT-BR, EM TÓPICOS]"
    if USE_GROQ_LIB:
        r = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":sistema},{"role":"user","content":prompt}],
            temperature=0.6,
            max_tokens=400
        )
        return r.choices[0].message.content
    else:
        import urllib.request
        url = "https://api.groq.com/openai/v1/chat/completions"
        data = json.dumps({
            "model":"llama-3.1-8b-instant",
            "messages":[{"role
