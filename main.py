from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from crewai import Agent, Task, Crew
import os
import asyncio

# Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7504265835:AAGkAEHaMmBW59SlfQ0ga9XuUF-lsx83zRU")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sua_openai_api_key_aqui")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Cria o app Flask
app = Flask(__name__)

# Agente principal
interpretador = Agent(
    role="Agente de Ordens de Serviço",
    goal="Compreender e registrar solicitações de serviço",
    backstory="Você é um agente de hotelaria que interpreta mensagens dos hóspedes e registra apenas quando a mensagem contém uma solicitação de serviço clara.",
    model="gpt-4o",
    verbose=False
)

# Função de interpretação com CrewAI
async def interpretar_mensagem(texto):
    prompt = f"""
    Analise a seguinte mensagem e diga se é uma ordem de serviço (OS). Se for, extraia os seguintes campos:
    - nome
    - quarto
    - data
    - hora
    - tipo
    - detalhes
    - prioridade
    Se não for uma OS, apenas diga: "Conversa registrada. Nenhuma OS identificada.".

    Mensagem: "{texto}"
    """

    task = Task(
        description=prompt,
        expected_output="Um JSON com os campos da OS ou uma resposta simples.",
        agent=interpretador
    )

    resultado = Crew(agents=[interpretador], tasks=[task]).kickoff()
    return resultado

# Manipulador de mensagens no Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    resposta = await interpretar_mensagem(texto)
    await update.message.reply_text(resposta)

# Rota raiz apenas para teste do servidor
@app.route("/")
def index():
    return "Servidor do bot de hotel online."

# Função para rodar o bot
def iniciar_bot():
    app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot iniciado...")
    app_bot.run_polling()

# Inicializa o bot em paralelo ao Flask
if __name__ == '__main__':
    from threading import Thread
    Thread(target=iniciar_bot).start()
    app.run(host='0.0.0.0', port=8080)

