import csv
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI


# =========================
# CONFIGURAÇÕES
# =========================

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "A chave OPENROUTER_API_KEY não foi encontrada no arquivo .env."
    )

MODEL_ID = "openai/gpt-4.1"

TEMPERATURE = 0.2
MAX_TOKENS = 160

ARQUIVO_PERSONAS = "personas.csv"
ARQUIVO_LOG = "logs.txt"
ARQUIVO_FIGURA = "logs_figura.txt"

ESTRATEGIAS = [
    "CONFRONTO",
    "VALIDAÇÃO"
]

# True: executa somente os cenários da persona Maria.
# False: executa todos os cenários cadastrados no personas.csv.
MODO_PILOTO = False

client = OpenAI(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# =========================
# LEITURA DAS PERSONAS
# =========================

def carregar_personas(caminho):
    campos_obrigatorios = [
        "Nome",
        "Idade",
        "Estagio",
        "Sintoma",
        "Cenario",
        "Gatilho",
        "ContextoObjetivo"
    ]

    with open(
        caminho,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as arquivo:

        amostra = arquivo.read(2048)
        arquivo.seek(0)

        try:
            dialecto = csv.Sniffer().sniff(
                amostra,
                delimiters=",;"
            )
        except csv.Error:
            dialecto = csv.excel

        leitor = csv.DictReader(
            arquivo,
            dialect=dialecto
        )

        if not leitor.fieldnames:
            raise RuntimeError(
                "O arquivo personas.csv não possui cabeçalho."
            )

        campos_faltantes = [
            campo
            for campo in campos_obrigatorios
            if campo not in leitor.fieldnames
        ]

        if campos_faltantes:
            raise RuntimeError(
                "Campos ausentes no personas.csv: "
                + ", ".join(campos_faltantes)
            )

        personas = []

        for numero_linha, linha in enumerate(
            leitor,
            start=2
        ):
            registro = {
                campo: (
                    linha.get(campo) or ""
                ).strip()
                for campo in campos_obrigatorios
            }

            # Ignora linhas completamente vazias.
            if not any(registro.values()):
                continue

            campos_vazios = [
                campo
                for campo, valor in registro.items()
                if not valor
            ]

            if campos_vazios:
                raise RuntimeError(
                    f"Linha {numero_linha} do personas.csv "
                    f"possui campos vazios: "
                    + ", ".join(campos_vazios)
                )

            personas.append(registro)

    if not personas:
        raise RuntimeError(
            "Nenhuma persona foi encontrada no arquivo personas.csv."
        )

    return personas


# =========================
# CONSTRUÇÃO DO PROMPT
# =========================

def montar_prompt(persona, estrategia):
    nome = persona["Nome"]
    idade = persona["Idade"]
    estagio = persona["Estagio"]
    sintoma = persona["Sintoma"]
    cenario = persona["Cenario"]
    gatilho = persona["Gatilho"]
    contexto_objetivo = persona["ContextoObjetivo"]

    if estrategia == "CONFRONTO":
        instrucao = (
             "A resposta do familiar deve utilizar uma estratégia de confronto. "
             "Responda de forma direta à fala ou percepção apresentada pela persona, "
             "corrigindo a informação quando houver um fato objetivo disponível. "
             "Mantenha um tom respeitoso, sem acolher ou validar previamente a percepção apresentada."
        )

    elif estrategia == "VALIDAÇÃO":
        instrucao = (
             "A resposta do familiar deve utilizar uma estratégia de validação. "
             "Acolha a fala, a dificuldade ou a emoção apresentada pela persona, "
             "sem confirmar como verdadeiro um fato que seja contradito pelo "
             "contexto objetivo do cenário. Em seguida, redirecione a situação "
             "de maneira calma."
    )
    else:
        raise ValueError(
            f"Estratégia inválida: {estrategia}"
        )

    return f"""
Você participa de uma ferramenta educacional destinada a familiares de pessoas com Doença de Alzheimer. A ferramenta simula situações de cuidado para comparar diferentes estratégias de comunicação.

Dados da persona:

Nome: {nome}
Idade: {idade}
Estágio da doença: {estagio}
Sintoma principal: {sintoma}
Cenário simulado: {cenario}
Fala inicial da persona: {gatilho}
Contexto objetivo do cenário: {contexto_objetivo}

Estratégia de comunicação: {estrategia}

{instrucao}

Sua tarefa possui duas partes:

1. Gere uma fala curta que o familiar poderia dizer à persona utilizando a estratégia de comunicação indicada.

2. Em seguida, simule uma reação plausível da persona ao ouvir a fala do familiar.

Para gerar a reação da persona:

- considere o estágio da doença, o sintoma e o cenário apresentados;

- considere o conteúdo da resposta recebida;

- não determine previamente que a reação será positiva ou negativa;

- não force a persona a ficar calma, irritada, ansiosa ou satisfeita;

- produza uma reação coerente com a situação apresentada.

Regras:

- Responda sempre em português do Brasil.

- A resposta do familiar deve conter no máximo duas frases.

- A reação da persona deve conter no máximo duas frases.

- Não explique a estratégia utilizada.

- Não acrescente análises ou justificativas.

- Não descreva ações entre parênteses.

- Não invente informações pessoais que não estejam presentes nos dados da persona.

- Não crie datas, nomes de familiares, locais, acontecimentos ou lembranças que não tenham sido fornecidos.

- Quando uma informação não estiver disponível, responda sem completar o dado por conta própria.

- Não afirme como verdadeiro nenhum fato que não esteja explicitamente presente nos dados da persona ou do cenário. Quando uma informação não for fornecida, não complete, suponha ou invente essa informação.

- Não utilize insultos, ameaças, ironia ou linguagem coercitiva.

- Na estratégia de validação, não confirme como verdadeiro um fato que o contexto objetivo indique ser incorreto.

- Quando a informação solicitada pela persona não estiver disponível no contexto, não invente uma justificativa para sua ausência e não atribua ao familiar desconhecimento, esquecimento ou qualquer outra condição não informada.

Utilize obrigatoriamente o seguinte formato:

RESPOSTA_FAMILIAR:
[fala do familiar]

REACAO_PERSONA:
[reação da persona]
""".strip()


# =========================
# TRATAMENTO DA RESPOSTA
# =========================

def extrair_interacao(texto):
    if not texto:
        raise RuntimeError(
            "O modelo não retornou uma resposta textual."
        )

    texto = texto.strip()

    marcador_resposta = "RESPOSTA_FAMILIAR:"
    marcador_reacao = "REACAO_PERSONA:"

    if (
        marcador_resposta not in texto
        or marcador_reacao not in texto
    ):
        raise RuntimeError(
            "A resposta do modelo não seguiu o formato esperado."
        )

    conteudo = texto.split(
        marcador_resposta,
        1
    )[1]

    resposta_familiar, reacao_persona = conteudo.split(
        marcador_reacao,
        1
    )

    resposta_familiar = resposta_familiar.strip()
    reacao_persona = reacao_persona.strip()

    resposta_familiar = " ".join(
        resposta_familiar.split()
    )

    reacao_persona = " ".join(
        reacao_persona.split()
    )

    return resposta_familiar, reacao_persona


# =========================
# CHAMADA À LLM
# =========================

def gerar_resposta_llm(persona, estrategia):
    prompt = montar_prompt(
        persona,
        estrategia
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você participa de uma simulação educacional "
                        "sobre estratégias de comunicação relacionadas "
                        "à Doença de Alzheimer. Gere a resposta do familiar "
                        "e uma reação plausível da persona sem determinar "
                        "previamente o resultado emocional da interação. "
                        "Siga rigorosamente o formato solicitado."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

        conteudo = (
            response
            .choices[0]
            .message
            .content
        )

        return extrair_interacao(
            conteudo
        )

    except Exception as erro:
        raise RuntimeError(
            f"Falha ao gerar interação para "
            f"{persona['Nome']} — "
            f"{persona['Cenario']} — "
            f"{estrategia}: {erro}"
        ) from erro


# =========================
# EXECUÇÃO DAS SIMULAÇÕES
# =========================

def registrar_simulacao():
    personas = carregar_personas(
        ARQUIVO_PERSONAS
    )

    if MODO_PILOTO:
        personas = [
            persona
            for persona in personas
            if persona["Nome"] == "Maria"
        ]

        if not personas:
            raise RuntimeError(
                "A persona Maria não foi encontrada no arquivo personas.csv."
            )

    total_chamadas = (
        len(personas)
        * len(ESTRATEGIAS)
    )

    if MODO_PILOTO:
        print(
            f"MODO PILOTO: serão realizadas "
            f"{total_chamadas} chamadas à API."
        )

    else:
        print(
            f"MODO COMPLETO: serão realizadas "
            f"{total_chamadas} chamadas à API."
        )

    linhas_log = [
        "REGISTRO DAS SIMULAÇÕES",
        (
            "Data de execução: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ),
        f"Modelo de linguagem: {MODEL_ID}",
        "Plataforma de acesso: OpenRouter",
        f"Temperature: {TEMPERATURE}",
        f"Max tokens: {MAX_TOKENS}",
        f"Quantidade de cenários: {len(personas)}",
        (
            "Estratégias avaliadas: "
            + ", ".join(ESTRATEGIAS)
        ),
        (
            "Ferramenta educacional para "
            "orientação de familiares"
        ),
        "=" * 60,
        ""
    ]

    respostas_geradas = {}

    for persona in personas:
        nome = persona["Nome"]
        idade = persona["Idade"]
        estagio = persona["Estagio"]
        sintoma = persona["Sintoma"]
        cenario = persona["Cenario"]
        gatilho = persona["Gatilho"]
        contexto_objetivo = (
            persona["ContextoObjetivo"]
        )

        linhas_log.extend([
            f"Persona: {nome}",
            f"Idade: {idade}",
            f"Estágio: {estagio}",
            f"Sintoma: {sintoma}",
            f"Cenário: {cenario}",
            "",
            f"Fala inicial da persona: {gatilho}",
            (
                "Contexto objetivo: "
                f"{contexto_objetivo}"
            ),
            ""
        ])

        for estrategia in ESTRATEGIAS:
            print(
                f"Gerando: {nome} — "
                f"{sintoma} — "
                f"{estrategia}"
            )

            resposta_familiar, reacao_persona = (
                gerar_resposta_llm(
                    persona,
                    estrategia
                )
            )

            respostas_geradas[
                (
                    nome,
                    cenario,
                    estrategia
                )
            ] = {
                "resposta_familiar": resposta_familiar,
                "reacao_persona": reacao_persona
            }

            linhas_log.append(
                f"[ESTRATÉGIA: {estrategia}]"
            )

            linhas_log.append(
                "Resposta sugerida ao familiar: "
                f"{resposta_familiar}"
            )

            linhas_log.append(
                "Reação simulada da persona: "
                f"{reacao_persona}"
            )

            linhas_log.append("")

        linhas_log.append(
            "-" * 60
        )

        linhas_log.append("")

    # =========================
    # LOG COMPLETO
    # =========================

    with open(
        ARQUIVO_LOG,
        "w",
        encoding="utf-8"
    ) as arquivo:
        arquivo.write(
            "\n".join(linhas_log)
        )

    # =========================
    # ARQUIVO REDUZIDO PARA FIGURA
    # =========================

    persona_figura = next(
        (
            persona
            for persona in personas
            if (
                persona["Nome"] == "Maria"
                and persona["Sintoma"] == "Paranoia leve"
            )
        ),
        None
    )

    figura_gerada = False

    if persona_figura is not None:
        nome_figura = persona_figura["Nome"]
        cenario_figura = persona_figura["Cenario"]

        chave_confronto = (
            nome_figura,
            cenario_figura,
            "CONFRONTO"
        )

        chave_validacao = (
            nome_figura,
            cenario_figura,
            "VALIDAÇÃO"
        )

        if (
            chave_confronto in respostas_geradas
            and chave_validacao in respostas_geradas
        ):
            exemplo = [
                "EXEMPLO DE REGISTRO DA SIMULAÇÃO",
                f"Modelo de linguagem: {MODEL_ID}",
                "Plataforma de acesso: OpenRouter",
                f"Temperature: {TEMPERATURE}",
                f"Max tokens: {MAX_TOKENS}",
                (
                    "Ferramenta educacional para "
                    "orientação de familiares"
                ),
                "=" * 60,
                "",
                (
                    "Persona: "
                    f"{persona_figura['Nome']}"
                ),
                (
                    "Idade: "
                    f"{persona_figura['Idade']}"
                ),
                (
                    "Estágio: "
                    f"{persona_figura['Estagio']}"
                ),
                (
                    "Sintoma: "
                    f"{persona_figura['Sintoma']}"
                ),
                (
                    "Cenário: "
                    f"{persona_figura['Cenario']}"
                ),
                "",
                (
                    "Fala inicial da persona: "
                    f"{persona_figura['Gatilho']}"
                ),
                "",
                "[ESTRATÉGIA: CONFRONTO]",
                (
                    "Resposta sugerida ao familiar: "
                    + respostas_geradas[
                        chave_confronto
                    ]["resposta_familiar"]
                ),
                (
                    "Reação simulada da persona: "
                    + respostas_geradas[
                        chave_confronto
                    ]["reacao_persona"]
                ),
                "",
                "[ESTRATÉGIA: VALIDAÇÃO]",
                (
                    "Resposta sugerida ao familiar: "
                    + respostas_geradas[
                        chave_validacao
                    ]["resposta_familiar"]
                ),
                (
                    "Reação simulada da persona: "
                    + respostas_geradas[
                        chave_validacao
                    ]["reacao_persona"]
                ),
                ""
            ]

            with open(
                ARQUIVO_FIGURA,
                "w",
                encoding="utf-8"
            ) as arquivo:
                arquivo.write(
                    "\n".join(exemplo)
                )

            figura_gerada = True

    print("")
    print("Simulação concluída.")
    print(
        f"Arquivo completo gerado: {ARQUIVO_LOG}"
    )

    if figura_gerada:
        print(
            f"Arquivo para figura gerado: "
            f"{ARQUIVO_FIGURA}"
        )
    else:
        print(
            "Arquivo para figura não foi gerado, "
            "pois o cenário Maria / Paranoia leve "
            "não foi encontrado."
        )


if __name__ == "__main__":
    registrar_simulacao()
