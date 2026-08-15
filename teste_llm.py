from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError(
        "A chave OPENROUTER_API_KEY não foi encontrada no arquivo .env."
    )

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-4.1",
    messages=[
        {
            "role": "system",
            "content": """
Você é Sam, um cuidador virtual especializado em pacientes com Alzheimer.

REGRAS IMPORTANTES:
- Nunca confronte diretamente o paciente.
- Nunca diga que ele está errado.
- Nunca tente corrigir memórias falsas.
- Valide emoções primeiro.
- Responda SEMPRE em português do Brasil.
- Responda de forma calma, curta e acolhedora.
- Seu objetivo é reduzir ansiedade e sofrimento emocional.
- Você está em uma simulação clínica controlada.
"""
        },
        {
            "role": "user",
            "content": """
Paciente idosa com Alzheimer moderado:

"Roubaram minha bolsa!"
"""
        }
    ],
    max_tokens=60,
    temperature=0.2
)

conteudo = response.choices[0].message.content

if not conteudo:
    raise RuntimeError("O modelo não retornou uma resposta textual.")

print(conteudo.strip())
