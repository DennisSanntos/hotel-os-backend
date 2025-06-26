from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew
import os
import ast

app = Flask(__name__)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "chave_openai_aqui")

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

    resultado = Crew(agents=[interpretador], tasks=[task]).kickoff()

    # Converte string retornada para dicionário
    json_resultado = ast.literal_eval(resultado)
    return jsonify({"resultado": json_resultado})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

