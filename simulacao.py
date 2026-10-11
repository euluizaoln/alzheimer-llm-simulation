"""Controlador principal das simulações."""

import csv
import uuid
from datetime import datetime
from pathlib import Path

from llm import MODEL_ID, TEMPERATURE, MAX_TOKENS, chamar_llm
from prompts import (
    montar_prompt_estado,
    montar_prompt_familiar,
    montar_prompt_persona,
    montar_prompt_persona_primeiro,
    montar_prompt_familiar_apos_persona,
    montar_prompt_estado_persona_primeiro,
)

BASE_DIR = Path(__file__).resolve().parent

ARQUIVO_PERSONAS = BASE_DIR / "personas.csv"
ARQUIVO_LOG = BASE_DIR / "logs.txt"

MAX_RODADAS = 5
REQUISICOES_POR_RODADA = 3

CAMPOS_OBRIGATORIOS = [
    "Nome",
    "Idade",
    "Profissao",
    "EstadoCivil",
    "Filhos",
    "Familiar",
    "CaracteristicasPessoais",
    "Estagio",
    "Sintoma",
    "Cenario",
    "Situacao",
    "ContextoObjetivo",
]


# ============================================================
# DADOS
# ============================================================

def carregar_personas(caminho):
    """Carrega e valida os registros do arquivo personas.csv."""
    with open(
        caminho,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        if not leitor.fieldnames:
            raise RuntimeError(
                "O arquivo personas.csv não possui cabeçalho."
            )

        faltantes = [
            campo
            for campo in CAMPOS_OBRIGATORIOS
            if campo not in leitor.fieldnames
        ]

        if faltantes:
            raise RuntimeError(
                "Campos ausentes no personas.csv: "
                + ", ".join(faltantes)
            )

        personas = []

        for numero_linha, linha in enumerate(leitor, start=2):
            registro = {
                campo: (linha.get(campo) or "").strip()
                for campo in CAMPOS_OBRIGATORIOS
            }

            if not any(registro.values()):
                continue

            vazios = [
                campo
                for campo, valor in registro.items()
                if not valor
            ]

            if vazios:
                raise RuntimeError(
                    f"Linha {numero_linha} possui campos vazios: "
                    + ", ".join(vazios)
                )

            personas.append(registro)

    if not personas:
        raise RuntimeError(
            "Nenhuma persona foi encontrada no arquivo personas.csv."
        )

    return personas


# ============================================================
# MENU
# ============================================================

def escolher_persona(personas):
    """Permite escolher uma persona sem repetir seus dois cenários."""
    grupos = {}

    for persona in personas:
        grupos.setdefault(persona["Nome"], persona)

    nomes = list(grupos.keys())

    print("\n" + "=" * 60)
    print("PERSONAS DISPONÍVEIS")
    print("=" * 60)

    for indice, nome in enumerate(nomes, start=1):
        persona = grupos[nome]
        print(
            f"{indice}. {nome} "
            f"({persona['Estagio']})"
        )

    while True:
        escolha = input("\nEscolha a persona: ").strip()

        try:
            indice = int(escolha)

            if 1 <= indice <= len(nomes):
                nome_escolhido = nomes[indice - 1]

                return [
                    persona
                    for persona in personas
                    if persona["Nome"] == nome_escolhido
                ]

        except ValueError:
            pass

        print("Escolha inválida.")


def escolher_cenario(personas_da_persona):
    """Permite escolher um dos cenários associados à persona."""
    nome = personas_da_persona[0]["Nome"]

    print("\n" + "=" * 60)
    print(f"CENÁRIOS DE {nome.upper()}")
    print("=" * 60)

    for indice, persona in enumerate(
        personas_da_persona,
        start=1,
    ):
        print(f"{indice}. {persona['Cenario']}")
        print(f"   Sintoma: {persona['Sintoma']}")

    while True:
        escolha = input("\nEscolha o cenário: ").strip()

        try:
            indice = int(escolha)

            if 1 <= indice <= len(personas_da_persona):
                return personas_da_persona[indice - 1]

        except ValueError:
            pass

        print("Escolha inválida.")


def escolher_estrategia():
    """Permite escolher a estratégia experimental."""
    print("\n" + "=" * 60)
    print("ESTRATÉGIA DE COMUNICAÇÃO")
    print("=" * 60)
    print("1. CONFRONTO")
    print("2. VALIDAÇÃO")

    while True:
        escolha = input("\nEscolha a estratégia: ").strip()

        if escolha == "1":
            return "CONFRONTO"

        if escolha == "2":
            return "VALIDAÇÃO"

        print("Escolha inválida.")


# ============================================================
# ESTADO
# ============================================================

def criar_estado(persona):
    """Cria o estado inicial da conversa."""
    return {
        "rodada": 0,
        "situacao_atual": persona["Situacao"],
        "mudanca": "Início da interação.",
        "ultima_fala_familiar": "",
        "ultima_reacao_persona": "",
    }


def interpretar_estado(resposta, estado_anterior):
    """Extrai SITUACAO e MUDANCA da terceira resposta da LLM."""
    situacao_atual = estado_anterior["situacao_atual"]
    mudanca = "Nenhuma mudança relevante."

    texto = resposta.strip()
    texto_upper = texto.upper()

    pos_situacao = texto_upper.find("SITUACAO:")
    pos_mudanca = texto_upper.find("MUDANCA:")

    if pos_situacao >= 0:
        inicio = pos_situacao + len("SITUACAO:")
        fim = (
            pos_mudanca
            if pos_mudanca > inicio
            else len(texto)
        )
        valor = texto[inicio:fim].strip(" -|")
        if valor:
            situacao_atual = valor

    if pos_mudanca >= 0:
        valor = texto[
            pos_mudanca + len("MUDANCA:")
        :].strip(" -|")

        if valor:
            mudanca = valor

    return situacao_atual, mudanca


def persona_inicia_rodada(persona):
    """Define cenários em que a persona apresenta o problema antes do familiar."""
    cenario = persona["Cenario"].strip().lower()
    return (
        persona["Nome"].strip().upper() == "MARIA"
        and ("bolsa" in cenario or "ateli" in cenario)
    )


# ============================================================
# TRÊS REQUISIÇÕES DE CADA RODADA
# ============================================================

def gerar_fala_persona_primeiro(
    persona,
    estrategia,
    historico,
    estado,
):
    """Requisição 1/3 quando a persona inicia a rodada."""
    prompt = montar_prompt_persona_primeiro(
        persona,
        estrategia,
        historico,
        estado,
    )
    return chamar_llm(
        prompt,
        (
            "Você representa somente a persona sintética. "
            "Gere apenas a fala da persona que inicia a rodada."
        ),
    )


def gerar_fala_familiar_apos_persona(
    persona,
    estrategia,
    fala_persona,
    historico,
    estado,
):
    """Requisição 2/3 quando o familiar responde à persona."""
    prompt = montar_prompt_familiar_apos_persona(
        persona,
        estrategia,
        fala_persona,
        historico,
        estado,
    )
    return chamar_llm(
        prompt,
        (
            "Você representa somente o familiar da persona. "
            "Responda diretamente à fala atual da persona."
        ),
    )


def atualizar_estado_persona_primeiro(
    persona,
    historico,
    estado,
    fala_persona,
    fala_familiar,
):
    """Requisição 3/3 quando a persona falou primeiro."""
    prompt = montar_prompt_estado_persona_primeiro(
        persona,
        historico,
        estado,
        fala_persona,
        fala_familiar,
    )
    resposta = chamar_llm(
        prompt,
        (
            "Você atualiza o estado de uma simulação educacional. "
            "Retorne somente SITUACAO e MUDANCA."
        ),
    )
    situacao_atual, mudanca = interpretar_estado(resposta, estado)
    return {
        "rodada": estado["rodada"] + 1,
        "situacao_atual": situacao_atual,
        "mudanca": mudanca,
        "ultima_fala_familiar": fala_familiar,
        "ultima_reacao_persona": fala_persona,
    }


def gerar_fala_familiar(
    persona,
    estrategia,
    historico,
    estado,
):
    """Requisição 1/3: resposta sugerida ao familiar."""
    prompt = montar_prompt_familiar(
        persona,
        estrategia,
        historico,
        estado,
    )

    return chamar_llm(
        prompt,
        (
            "Você representa o familiar da persona durante uma simulação "
            f"educacional. O vínculo familiar é: {persona['Familiar']}. "
            "Gere somente a fala desse familiar e siga rigorosamente "
            "a estratégia de comunicação informada."
        ),
    )


def gerar_reacao_persona(
    persona,
    estrategia,
    fala_familiar,
    historico,
    estado,
):
    """Requisição 2/3: reação simulada da persona."""
    prompt = montar_prompt_persona(
        persona,
        estrategia,
        fala_familiar,
        historico,
        estado,
    )

    return chamar_llm(
        prompt,
        (
            "Você representa somente a persona sintética. Gere "
            "apenas a reação da persona e não explique o processo."
        ),
    )


def atualizar_estado(
    persona,
    historico,
    estado,
    fala_familiar,
    reacao_persona,
):
    """Requisição 3/3: situação atual e mudança observada."""
    prompt = montar_prompt_estado(
        persona=persona,
        historico=historico,
        estado=estado,
        fala_familiar=fala_familiar,
        reacao_persona=reacao_persona,
    )

    resposta = chamar_llm(
        prompt,
        (
            "Você atualiza o estado de uma simulação educacional. "
            "Retorne somente SITUACAO e MUDANCA."
        ),
    )

    situacao_atual, mudanca = interpretar_estado(
        resposta,
        estado,
    )

    return {
        "rodada": estado["rodada"] + 1,
        "situacao_atual": situacao_atual,
        "mudanca": mudanca,
        "ultima_fala_familiar": fala_familiar,
        "ultima_reacao_persona": reacao_persona,
    }


# ============================================================
# LOG
# ============================================================

def registrar_inicio_simulacao(
    arquivo,
    simulacao_id,
    persona,
    estrategia,
):
    """Registra os metadados e o perfil fixo da execução."""
    arquivo.write("=" * 72 + "\n")
    arquivo.write(f"SIMULAÇÃO: {simulacao_id}\n")
    arquivo.write(
        "Data: "
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + "\n"
    )
    arquivo.write(f"Modelo: {MODEL_ID}\n")
    arquivo.write(f"Temperature: {TEMPERATURE}\n")
    arquivo.write(f"Max tokens: {MAX_TOKENS}\n")
    arquivo.write(f"Máximo de rodadas: {MAX_RODADAS}\n")
    arquivo.write(
        f"Requisições ao modelo por rodada: "
        f"{REQUISICOES_POR_RODADA}\n"
    )
    arquivo.write(f"Persona: {persona['Nome']}\n")
    arquivo.write(f"Idade: {persona['Idade']}\n")
    arquivo.write(f"Profissão: {persona['Profissao']}\n")
    arquivo.write(
        f"Estado civil: {persona['EstadoCivil']}\n"
    )
    arquivo.write(f"Filhos: {persona['Filhos']}\n")
    arquivo.write(f"Familiar responsável: {persona['Familiar']}\n")
    arquivo.write(
        "Características pessoais: "
        f"{persona['CaracteristicasPessoais']}\n"
    )
    arquivo.write(f"Estágio: {persona['Estagio']}\n")
    arquivo.write(f"Sintoma: {persona['Sintoma']}\n")
    arquivo.write(f"Cenário: {persona['Cenario']}\n")
    arquivo.write(f"Estratégia: {estrategia}\n")
    arquivo.write(f"Situação: {persona['Situacao']}\n")
    arquivo.write(
        f"Contexto objetivo: "
        f"{persona['ContextoObjetivo']}\n\n"
    )


def registrar_interacao(
    arquivo,
    persona,
    estado,
    fala_familiar,
    reacao_persona,
    persona_primeiro=False,
):
    """Registra uma rodada respeitando a ordem real dos participantes."""
    arquivo.write("-" * 72 + "\n")
    arquivo.write(f"RODADA {estado['rodada']}\n\n")

    if persona_primeiro:
        arquivo.write(
            f"[1/3] FALA DA PERSONA ({persona['Nome']})\n"
            f"{reacao_persona}\n\n"
        )
        arquivo.write(
            f"[2/3] RESPOSTA DO FAMILIAR ({persona['Familiar']})\n"
            f"{fala_familiar}\n\n"
        )
    else:
        arquivo.write(
            f"[1/3] RESPOSTA DO FAMILIAR ({persona['Familiar']})\n"
            f"{fala_familiar}\n\n"
        )
        arquivo.write(
            f"[2/3] REAÇÃO DA PERSONA\n"
            f"{reacao_persona}\n\n"
        )

    arquivo.write(
        f"[3/3] ATUALIZAÇÃO DO ESTADO\n"
        f"Situação atual: {estado['situacao_atual']}\n"
        f"Mudança: {estado['mudanca']}\n"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

def exibir_resumo_persona(persona, estrategia):
    """Mostra no terminal as informações fixas da simulação."""
    print("\n" + "=" * 60)
    print("SIMULAÇÃO INICIADA")
    print("=" * 60)
    print(f"Persona: {persona['Nome']}")
    print(f"Idade: {persona['Idade']}")
    print(f"Profissão: {persona['Profissao']}")
    print(f"Estado civil: {persona['EstadoCivil']}")
    print(f"Filhos: {persona['Filhos']}")
    print(f"Familiar: {persona['Familiar']}")
    print(
        "Características pessoais: "
        f"{persona['CaracteristicasPessoais']}"
    )
    print(f"Estágio: {persona['Estagio']}")
    print(f"Sintoma: {persona['Sintoma']}")
    print(f"Cenário: {persona['Cenario']}")
    print(f"Estratégia: {estrategia}")
    print(f"\nSituação: {persona['Situacao']}")
    print(
        f"\nCada rodada possui "
        f"{REQUISICOES_POR_RODADA} requisições sequenciais."
    )
    print(
        f"A simulação terá "
        f"{MAX_RODADAS} rodadas."
    )


def executar_simulacao(
    persona,
    estrategia,
    simulacao_id,
):
    """Executa uma simulação completa de cinco rodadas."""
    historico = []
    estado = criar_estado(persona)

    exibir_resumo_persona(persona, estrategia)

    with open(
        ARQUIVO_LOG,
        "a",
        encoding="utf-8",
    ) as arquivo_log:

        registrar_inicio_simulacao(
            arquivo=arquivo_log,
            simulacao_id=simulacao_id,
            persona=persona,
            estrategia=estrategia,
        )

        for numero_rodada in range(
            1,
            MAX_RODADAS + 1,
        ):
            print(
                "\n"
                + "=" * 60
                + f"\nRODADA {numero_rodada}\n"
                + "=" * 60
            )

            persona_primeiro = persona_inicia_rodada(persona)

            if persona_primeiro:
                print("[1/3] ")
                reacao_persona = gerar_fala_persona_primeiro(
                    persona=persona,
                    estrategia=estrategia,
                    historico=historico,
                    estado=estado,
                )
                print(f"{persona['Nome']}: {reacao_persona}")

                print("\n[2/3]")
                fala_familiar = gerar_fala_familiar_apos_persona(
                    persona=persona,
                    estrategia=estrategia,
                    fala_persona=reacao_persona,
                    historico=historico,
                    estado=estado,
                )
                print(f"{persona['Familiar']}: {fala_familiar}")

                print("\n[3/3]")
                novo_estado = atualizar_estado_persona_primeiro(
                    persona=persona,
                    historico=historico,
                    estado=estado,
                    fala_persona=reacao_persona,
                    fala_familiar=fala_familiar,
                )
            else:
                print("[1/3] ")
                fala_familiar = gerar_fala_familiar(
                    persona=persona,
                    estrategia=estrategia,
                    historico=historico,
                    estado=estado,
                )
                print(f"{persona['Familiar']}: {fala_familiar}")

                print("\n[2/3]")
                reacao_persona = gerar_reacao_persona(
                    persona=persona,
                    estrategia=estrategia,
                    fala_familiar=fala_familiar,
                    historico=historico,
                    estado=estado,
                )
                print(f"{persona['Nome']}: {reacao_persona}")

                print("\n[3/3]")
                novo_estado = atualizar_estado(
                    persona=persona,
                    historico=historico,
                    estado=estado,
                    fala_familiar=fala_familiar,
                    reacao_persona=reacao_persona,
                )

            historico.append(
                {
                    "rodada": novo_estado["rodada"],
                    "fala_familiar": fala_familiar,
                    "reacao_persona": reacao_persona,
                    "persona_primeiro": persona_primeiro,
                }
            )

            estado = novo_estado

            print(
                f"Situação atual: "
                f"{estado['situacao_atual']}"
            )
            print(
                f"Mudança: "
                f"{estado['mudanca']}"
            )

            registrar_interacao(
                arquivo=arquivo_log,
                persona=persona,
                estado=estado,
                fala_familiar=fala_familiar,
                reacao_persona=reacao_persona,
                persona_primeiro=persona_primeiro,
            )

        arquivo_log.write("-" * 72 + "\n")
        arquivo_log.write(
            f"FIM DA SIMULAÇÃO {simulacao_id}\n"
        )
        arquivo_log.write(
            f"Total de rodadas: "
            f"{estado['rodada']}\n"
        )
        arquivo_log.write(
            f"Total máximo de requisições ao modelo: "
            f"{estado['rodada'] * REQUISICOES_POR_RODADA}\n\n"
        )

    print("\n" + "=" * 60)
    print("SIMULAÇÃO FINALIZADA")
    print("=" * 60)
    print(f"Total de rodadas: {estado['rodada']}")
    print(
        "Total de requisições ao modelo: "
        f"{estado['rodada'] * REQUISICOES_POR_RODADA}"
    )


def main():
    personas = carregar_personas(
        ARQUIVO_PERSONAS
    )

    personas_da_persona = escolher_persona(
        personas
    )

    persona = escolher_cenario(
        personas_da_persona
    )

    estrategia = escolher_estrategia()

    simulacao_id = (
        datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_"
        + uuid.uuid4().hex[:6]
    )

    try:
        executar_simulacao(
            persona=persona,
            estrategia=estrategia,
            simulacao_id=simulacao_id,
        )

    except KeyboardInterrupt:
        print("\n\nSimulação encerrada pelo usuário.")

    except Exception as erro:
        print("\n\nERRO:")
        print(erro)


if __name__ == "__main__":
    main()
