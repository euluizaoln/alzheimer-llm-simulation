"""Construção dos prompts usados em cada rodada da simulação."""

INSTRUCOES_ESTRATEGIA = {
    "CONFRONTO": (
        "Responda de forma direta e respeitosa. Corrija explicitamente a "
        "percepção incorreta da persona usando somente os fatos objetivos "
        "fornecidos no perfil, na situação ou no contexto objetivo. A correção "
        "direta deve ser o elemento principal da resposta. Não utilize acolhimento "
        "como estratégia principal e não confirme como verdadeiro o fato incorreto. "
        "Não invente informações."
    ),
    "VALIDAÇÃO": (
        "Acolha primeiro a preocupação, a dificuldade ou a percepção apresentada "
        "pela persona. Evite iniciar a resposta com uma correção direta. Depois do "
        "acolhimento, conduza ou redirecione a interação de forma calma, sem confirmar "
        "como verdadeiro um fato que o contexto objetivo indica ser incorreto. "
        "Não invente informações."
    ),
}


def formatar_perfil_persona(persona):
    """Monta um bloco único e consistente com o perfil da persona."""
    return f"""Nome: {persona['Nome']}
Idade: {persona['Idade']}
Profissão: {persona['Profissao']}
Estado civil: {persona['EstadoCivil']}
Filhos: {persona['Filhos']}
Familiar responsável pela interação: {persona['Familiar']}
Características pessoais: {persona['CaracteristicasPessoais']}
Estágio: {persona['Estagio']}
Sintoma do cenário: {persona['Sintoma']}
Cenário: {persona['Cenario']}
Situação: {persona['Situacao']}
Contexto objetivo: {persona['ContextoObjetivo']}"""


def formatar_historico(historico):
    """Converte o histórico das rodadas anteriores em texto."""
    if not historico:
        return "Nenhuma interação anterior."

    linhas = []

    for interacao in historico:
        linhas.append(f"Rodada {interacao['rodada']}:")
        linhas.append(f"Familiar: {interacao['fala_familiar']}")
        linhas.append(f"Persona: {interacao['reacao_persona']}")

    return "\n".join(linhas)


def montar_prompt_familiar(persona, estrategia, historico, estado):
    """Prompt 1: gera a próxima fala sugerida ao familiar."""
    instrucao_estrategia = INSTRUCOES_ESTRATEGIA[estrategia]

    return f"""
Você participa de uma ferramenta educacional que simula interações entre
um familiar e uma persona sintética com características relacionadas à
Doença de Alzheimer.

TAREFA
Gere SOMENTE a próxima fala do familiar indicado no perfil.
Vínculo do familiar com a persona: {persona['Familiar']}.

PERFIL E CONTEXTO DA PERSONA
{formatar_perfil_persona(persona)}

ESTRATÉGIA DE COMUNICAÇÃO
{estrategia}

ORIENTAÇÃO DA ESTRATÉGIA
{instrucao_estrategia}

HISTÓRICO DA CONVERSA
{formatar_historico(historico)}

ESTADO ATUAL
Rodada em execução: {estado['rodada'] + 1}
Situação atual: {estado['situacao_atual']}
Mudança desde a rodada anterior: {estado['mudanca']}

Última fala do familiar:
{estado['ultima_fala_familiar'] or 'Nenhuma.'}

Última reação da persona:
{estado['ultima_reacao_persona'] or 'Nenhuma.'}

REGRAS
- Gere somente a fala do familiar.
- O familiar que fala é exatamente o indicado no perfil.
- Não altere nem invente outro grau de parentesco.
- Responda em português do Brasil.
- Use de duas a três frases, mantendo a fala natural e objetiva.
- A fala deve aplicar a estratégia indicada.
- Responda diretamente ao problema que está acontecendo naquele momento.
- Use uma linguagem simples, natural e fácil de compreender.
- Tenha apenas uma intenção principal por fala.
- Evite fazer várias perguntas na mesma resposta.
- Não transforme a conversa em uma entrevista.
- Considere o estágio, o sintoma, o cenário, a situação, o histórico e o estado atual.
- Use o perfil biográfico apenas quando ele for relevante para a situação.
- Não force referências à profissão, família ou personalidade.
- Continue a situação em vez de reiniciá-la ou repetir todo o contexto.
- Faça a conversa avançar gradualmente a cada rodada.
- Evite repetir frases ou estruturas usadas anteriormente.
- Use o contexto objetivo como referência factual da cena.
- Use somente fatos explicitamente presentes no perfil, na situação ou no contexto objetivo.
- Nunca deduza ou complete acontecimentos do passado da persona, mesmo que pareçam plausíveis.
- Ao corrigir a persona, utilize apenas fatos explicitamente fornecidos no perfil, na situação ou no contexto objetivo.
- Ao corrigir, repita ou parafraseie somente os fatos objetivos fornecidos.
- Não conclua que tarefas foram concluídas, obrigações foram cumpridas ou que algo está resolvido, a menos que isso esteja explicitamente informado.
- Não complete a história com acontecimentos anteriores que não foram informados.
- Não informe a localização, o estado ou a disponibilidade de objetos quando isso não estiver explicitamente descrito no perfil, na situação ou no contexto objetivo.
- Não escreva a reação da persona.
- Não explique a estratégia.
- Não faça análise.
- Não invente nomes, datas, locais, acontecimentos, lembranças, costumes, preferências ou fatos pessoais.
- Quando uma informação não estiver no perfil, na situação ou no contexto objetivo, não a invente.
- Não diga à persona que ela esqueceu, está esquecendo, não se lembra ou possui falha de memória.
- Corrija apenas o fato objetivo da situação, sem transformar a conversa em uma discussão sobre memória.
- Quando a persona não reconhecer o familiar, ele pode se identificar mas não pode ser pelo o nome e sim só como filho. 
- Não exija que a persona o reconheça e não pressione para que ela se lembre da relação familiar.
""".strip()


def montar_prompt_persona(persona, fala_familiar, historico, estado):
    """Prompt 2: gera a reação da persona à fala do familiar."""
    return f"""
Você participa de uma ferramenta educacional que simula uma conversa
entre um familiar e uma persona sintética relacionada à Doença de Alzheimer.

TAREFA
Gere SOMENTE a reação da persona à nova fala do familiar.

PERFIL E CONTEXTO DA PERSONA
{formatar_perfil_persona(persona)}

HISTÓRICO DA CONVERSA
{formatar_historico(historico)}

ESTADO ATUAL
Rodada em execução: {estado['rodada'] + 1}
Situação atual: {estado['situacao_atual']}
Mudança desde a rodada anterior: {estado['mudanca']}

NOVA FALA DO FAMILIAR
{fala_familiar}

REGRAS
- Gere somente a fala da persona.
- Considere que a fala recebida vem do familiar indicado no perfil.
- Não altere nem invente outro grau de parentesco.
- Responda em português do Brasil.
- Use de duas a três frases, mantendo a fala natural e objetiva.
- Reaja principalmente à última fala do familiar.
- Mantenha coerência com o perfil, estágio, sintoma, cenário e situação.
- Considere o histórico e o estado atual sem repetir toda a conversa.
- A reação deve ser simples, natural e continuar a situação de forma gradual.
- O perfil biográfico funciona como contexto, não como obrigação de mencionar esses dados.
- Use o contexto objetivo como referência factual da cena.
- A persona deve agir de acordo com a percepção descrita na situação.
- Não faça a persona corrigir espontaneamente a própria confusão.
- Não aceite automaticamente a correção do familiar apenas para encerrar a conversa.
- Mantenha coerência com a percepção do cenário e só mude de posição quando a própria interação justificar essa mudança.
- Qualquer mudança de posição deve acontecer gradualmente ao longo da conversa.
- A persona nunca deve dizer ou sugerir que está esquecendo, que esqueceu algo, que está confusa ou que possui uma falha de memória.
- A persona deve interpretar sua própria percepção como verdadeira naquele momento.
- Não crie outras pessoas, como clientes, colegas ou conhecidos, quando elas não estiverem explicitamente presentes na situação ou no contexto objetivo.
- Não acrescente consequências, acontecimentos ou detalhes que não tenham sido fornecidos.
- Não explique o que está fazendo.
- Não faça análise.
- Não mencione a estratégia de comunicação.
- Não invente nomes, datas, locais, acontecimentos, lembranças, costumes, preferências ou fatos pessoais.
- Quando uma informação não estiver no perfil, na situação ou no contexto objetivo, não a invente.
- Não determine previamente uma emoção específica.
- Não use rótulos emocionais como se fossem fatos.
- Não use expressões como "não lembro", "esqueci", "estou esquecendo", "será que esqueci", "minha memória", "estou confuso" ou equivalentes.
- Quando houver dúvida, expresse-a sobre a situação externa, e não sobre a própria memória.
- Exemplo permitido: "Tem alguma coisa que não está batendo."
- Exemplo proibido: "Será que estou esquecendo de alguma coisa?"
- Não diga que alguém está esperando pela persona, procurando por ela ou aguardando sua chegada, a menos que isso esteja explicitamente informado na situação ou no contexto objetivo.
- Quando a persona não reconhecer uma pessoa, não explique essa dificuldade como falha de memória.
- Não use expressões como "não me lembro de você", "esqueci quem você é" ou equivalentes.
- Não faça a persona perguntar por que não consegue reconhecer alguém.
- A persona deve simplesmente perceber a outra pessoa como desconhecida naquele momento.
- Prefira expressões como "eu não te conheço", "quem é você?" ou "por que você está aqui?".

""".strip()


def montar_prompt_estado(
    persona,
    historico,
    estado,
    fala_familiar,
    reacao_persona,
):
    """Prompt 3: atualiza situação e mudança após a interação da rodada."""
    return f"""
Você participa de uma ferramenta educacional que simula uma conversa
entre um familiar e uma persona sintética relacionada à Doença de Alzheimer.

TAREFA
Atualize o estado da conversa após a reação da persona.

PERFIL E CONTEXTO DA PERSONA
{formatar_perfil_persona(persona)}

ESTADO ANTERIOR
Situação:
{estado['situacao_atual']}

Mudança anterior:
{estado['mudanca']}

INTERAÇÃO DA RODADA ATUAL
Familiar ({persona['Familiar']}):
{fala_familiar}

Persona:
{reacao_persona}

HISTÓRICO DAS RODADAS ANTERIORES
{formatar_historico(historico)}

REGRAS
- Responda em português do Brasil.
- Retorne exatamente duas informações:
  SITUACAO: [situação atual]
  MUDANCA: [o que mudou desde o estado anterior]
- A SITUACAO deve resumir apenas o que permanece acontecendo agora.
- Não repita automaticamente ações da situação inicial.
- Descreva somente o que ainda está ocorrendo ou foi confirmado na rodada atual.
- A MUDANCA deve registrar somente uma mudança observável na interação.
- Se não houver mudança relevante, escreva: Nenhuma mudança relevante.
- Use a situação e o contexto objetivo como referência factual.
- Não invente acontecimentos, fatos pessoais ou mudanças que não tenham ocorrido.
- Não transforme suposições sobre memória, intenção ou emoção em fatos.
- Não determine emoções internas como fato.
- Não use rótulos emocionais como se fossem fatos.
- Não avalie qual estratégia é melhor.
- Não escreva novas falas.
- Seja breve e objetivo.
""".strip()

