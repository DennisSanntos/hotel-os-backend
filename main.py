from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os, ast, asyncio, threading

app = Flask(__name__)

# Token do seu bot do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7504265835:AAGkAEHaMmBW59SlfQ0ga9XuUF-lsx83zRU")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "sua-chave-aqui")
os.environ["OPENAI_API_KEY"] = OPENAI_KEY

# === Agente CrewAI ===
interpretador = Agent(
    role="Agente de Ordens de Serviço",
    goal="Interpretar OS em linguagem natural",
    backstory="Organiza OS de hotel com base em linguagem natural e decide se deve salvar",
    model="gpt-4o"
)

# === Endpoint para Apps Script ===
@app.route("/interpretar", methods=["POST"])
def interpretar():
    data = request.json
    texto = data.get("texto", "")
    return jsonify({"resultado": rodar_agente(texto)})

# === Função central para rodar o agente ===
def rodar_agente(texto):
    prompt = f"""
Você é um agente inteligente para registrar ordens de serviço de hotelaria. Responda de forma natural, e somente retorne um JSON se for uma ordem de serviço válida com:
- nome
- quarto
- data
- hora
- tipo
- detalhes
- prioridade

Frase: '{texto}'
    """

    task = Task(
        description=prompt,
        expected_output="Um JSON com os campos solicitados, apenas se a frase for uma OS válida.",
        agent=interpretador
    )

    resultado = Crew(agents=[interpretador], tasks=[task]).kickoff()

    try:
        json_resultado = ast.literal_eval(resultado.raw)
        return json_resultado
    except:
        return {"mensagem": resultado.raw}

# === Telegram handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    resposta = rodar_agente(texto)

    if isinstance(resposta, dict) and "nome" in resposta:
        mensagem = f"✅ OS para {resposta['nome']} no quarto {resposta['quarto']} às {resposta['hora']} de {resposta['data']}."
    else:
        mensagem = f"🤖 {resposta.get('mensagem', 'Não entendi, pode repetir?')}"

    await update.message.reply_text(mensagem)

# === Inicializar Telegram bot ===
def iniciar_bot_telegram():
    app_telegram = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_telegram.run_polling()

# Rodar Telegram em paralelo
threading.Thread(target=iniciar_bot_telegram).start()

# === Flask ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


