"""Teste simples de comunicação com o modelo via OpenRouter."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError(
        "A chave OPENROUTER_API_KEY não foi encontrada no arquivo .env."
    )

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
)

response = client.chat.completions.create(
    model="openai/gpt-4.1",
    messages=[
        {
            "role": "system",
            "content": (
                "Você participa de um teste técnico de comunicação com um modelo "
                "de linguagem. Responda em português do Brasil, de forma curta e objetiva."
            ),
        },
        {
            "role": "user",
            "content": "Responda apenas: conexão realizada com sucesso.",
        },
    ],
    max_tokens=60,
    temperature=0.2,
)

conteudo = response.choices[0].message.content

if not conteudo:
    raise RuntimeError("O modelo não retornou uma resposta textual.")

print(conteudo.strip())
