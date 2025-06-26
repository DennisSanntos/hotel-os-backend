from flask import Flask, request, jsonify
from crewai import Agent, Task, Crew
import os
import json

app = Flask(__name__)

# Usa variável de ambiente definida no Render
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "chave_openai_aqui")

# Define o agente
interpretador = Agent(
    role="Interpretador de Ordens de Serviço",
    goal="Extrair dados de OS em linguagem natural",
    backstory="Especialista em transformar textos livres em campos organizados para planilhas de hotelaria",
    model="gpt-4o",
    verbose=False
)

@app.route("/interpretar", methods=["POST"])
def interpretar():
    try:
        data = request.json
        texto = data.get("texto", "")

        prompt = f"""
Você é um assistente de hotelaria. Se o texto abaixo for uma solicitação válida de ordem de serviço (OS), extraia os campos em formato JSON:

- nome
- quarto
- data
- hora
- tipo
- detalhes
- prioridade

Caso o texto não represente uma OS válida (por exemplo: perguntas, saudações ou frases incompletas), **retorne apenas: {{"mensagem": "Sem OS detectada."}}**

Texto: '{texto}'
"""

        task = Task(
            description=prompt,
            expected_output="Um JSON com os campos solicitados ou mensagem de que não há OS.",
            agent=interpretador
        )

        resultado = Crew(agents=[interpretador], tasks=[task]).kickoff()

        # Tenta interpretar o retorno do modelo como JSON
        try:
            json_resultado = json.loads(resultado.raw)
        except Exception as e:
            return jsonify({
                "erro": "Falha ao interpretar JSON do agente.",
                "mensagem": str(e),
                "resultado_bruto": resultado.raw
            }), 500

        return jsonify({"resultado": json_resultado})

    except Exception as geral:
        return jsonify({"erro": "Erro inesperado no backend", "mensagem": str(geral)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

