from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew
import os
import json

app = Flask(__name__)

# Configure sua chave da OpenAI
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "chave_openai_aqui")

# Define o agente interpretador
interpretador = Agent(
    role="Interpretador de Ordens de Serviço",
    goal="Extrair dados de OS em linguagem natural",
    backstory="Especialista em transformar textos livres em campos organizados para planilhas de hotelaria",
    model="gpt-4o",
    verbose=False
)

@app.route("/interpretar", methods=["POST"])
def interpretar():
    data = request.json
    texto = data.get("texto", "")

    prompt = f"""Extraia da seguinte frase os campos abaixo em formato JSON:
    - nome
    - quarto
    - data
    - hora
    - tipo
    - detalhes
    - prioridade

    Frase: '{texto}'"""

    task = Task(
        description=prompt,
        expected_output="Um JSON com os campos solicitados.",
        agent=interpretador
    )

    try:
        crew = Crew(agents=[interpretador], tasks=[task])
        resultado = crew.kickoff()

        # Acessa a string JSON do resultado
        json_resultado = json.loads(resultado.raw)

        return jsonify({"resultado": json_resultado})
    except Exception as e:
        return jsonify({
            "erro": "Erro ao interpretar OS",
            "mensagem": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

