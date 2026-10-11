"""Camada responsável exclusivamente pela comunicação com o GPT-4.1."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL_ID = "openai/gpt-4.1"
TEMPERATURE = 0.2
MAX_TOKENS = 160

_client = None


def obter_client():
    """Cria o cliente da API somente quando ele for realmente necessário."""
    global _client

    if _client is not None:
        return _client

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "A variável OPENROUTER_API_KEY não foi encontrada no arquivo .env."
        )

    _client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    return _client


def chamar_llm(prompt, instrucao_sistema):
    """Envia uma requisição ao modelo e devolve somente o texto gerado."""
    try:
        client = obter_client()

        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": instrucao_sistema,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )

        conteudo = response.choices[0].message.content

        if not conteudo:
            raise RuntimeError("A LLM não retornou uma resposta.")

        return " ".join(conteudo.strip().split())

    except Exception as erro:
        raise RuntimeError(
            f"Falha na chamada à LLM: {erro}"
        ) from erro
