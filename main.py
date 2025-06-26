from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_OPENAI")

# Agente com capacidade de interpretação e decisão
interpretador = Agent(
    role="Agente de Hotelaria",
    goal="Conversar com o usuário e identificar se há uma ordem de serviço. Se houver, retornar os dados estruturados.",
    backstory=(
        "Você é um agente inteligente em um hotel. Seu trabalho é conversar com usuários, entender pedidos naturais "
        "e, apenas quando uma Ordem de Serviço (OS) for identificada, extrair seus campos em JSON para registro."
    ),
    verbose=True,
    model="gpt-4o"
)

@app.route("/interpretar", methods=["POST"])
def interpretar():
    try:
        data = request.get_json()
        texto = data.get("texto", "")

        prompt = f"""
        Analise a seguinte mensagem:
        \"\"\"{texto}\"\"\"

        Se a mensagem contiver uma ordem de serviço clara, retorne um JSON com os campos:
        - nome
        - quarto
        - data
        - hora
        - tipo
        - detalhes
        - prioridade

        Se a mensagem for apenas uma pergunta ou conversa comum, retorne:
        {{ "resposta": "<mensagem amigável e útil>" }}

        Nunca invente informações. Se algo estiver ausente, use string vazia ("").
        """

        tarefa = Task(
            description=prompt,
            expected_output="Um JSON com os campos da OS ou uma resposta comum.",
            agent=interpretador
        )

        resultado = Crew(agents=[interpretador], tasks=[tarefa]).kickoff()

        # Converte string para JSON
        json_resultado = json.loads(resultado.strip())
        return jsonify({"resultado": json_resultado})

    except Exception as e:
        return jsonify({
            "erro": "Erro ao interpretar mensagem",
            "mensagem": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
