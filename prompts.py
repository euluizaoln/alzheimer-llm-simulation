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
        "Reconheça brevemente a preocupação, a dificuldade ou a percepção apresentada "
        "pela persona e, em seguida, conduza ou redirecione a interação para uma ação "
        "simples e concreta no momento presente. Evite iniciar com uma correção direta, "
        "não prolongue a discussão sobre a percepção incorreta e não confirme como "
        "verdadeiro um fato que o contexto objetivo indica ser incorreto. "
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
        if interacao.get("persona_primeiro"):
            linhas.append(f"Persona: {interacao['reacao_persona']}")
            linhas.append(f"Familiar: {interacao['fala_familiar']}")
        else:
            linhas.append(f"Familiar: {interacao['fala_familiar']}")
            linhas.append(f"Persona: {interacao['reacao_persona']}")

    return "\n".join(linhas)


def instrucoes_linguagem_por_estagio(persona):
    """Define o nível de linguagem e de autoconsciência esperado em cada estágio."""
    estagio = persona["Estagio"].strip().upper()

    if "LEVE" in estagio:
        return """
- ESTÁGIO LEVE: a persona conversa de forma habitual, mas responde com uma única frase curta e natural. Ela pode reconhecer um lapso pontual ligado à situação atual.
- Ela pode dizer, de forma simples, que não está lembrando de algo específico ou que esqueceu uma tarefa concreta.
- Não faça a persona concluir que possui um problema de memória, que sua memória está piorando ou que o episódio ocorreu por causa da Doença de Alzheimer.
- Evite reflexões amplas sobre a própria condição cognitiva.
""".strip()

    if "MODER" in estagio:
        return """
- ESTÁGIO MODERADO: use preferencialmente uma frase curta, simples, direta e pouco elaborada.
- A persona pode sustentar a percepção apresentada no cenário, mesmo quando ela contradiz o contexto objetivo.
- Não faça a persona analisar a própria confusão ou explicar por que está interpretando a situação daquela forma.
- Quando o familiar redirecionar a conversa para outra ação concreta, permita que o foco mude gradualmente; não repita mecanicamente a mesma afirmação em todas as rodadas.
""".strip()

    if "AVAN" in estagio:
        return """
- ESTÁGIO AVANÇADO: use vocabulário muito reduzido, poucas palavras e frases muito curtas.
- Sempre que possível, responda com uma única frase curta ou com poucas palavras.
- Evite explicações, justificativas, reflexões, comparações e construções elaboradas.
- A persona pode responder de forma fragmentada, por exemplo: "Quem?", "Não.", "Casa.", "Quero ir.", "Tá.".
- Quando não reconhecer uma pessoa, não explique a dificuldade; apenas reaja como se aquela pessoa fosse desconhecida naquele momento.
""".strip()

    return "- Use linguagem simples e coerente com o estágio informado no perfil."


def instrucoes_especificas_joao(persona, estrategia):
    """Aplica ao João as orientações fornecidas pela profissional avaliadora."""
    if persona["Nome"].strip().upper() != "JOÃO":
        return "Nenhuma orientação específica adicional para esta persona."

    cenario = persona["Cenario"].strip().lower()

    if "oficina" in cenario:
        if estrategia == "CONFRONTO":
            return """
- Baseie a interação no exemplo fornecido pela profissional avaliadora para o estágio leve.
- A dificuldade de João é pontual: ele sabe o que é uma chave de roda, mas naquele momento não consegue reconhecer qual das ferramentas é a chave de roda.
- Use UMA ÚNICA frase curta por rodada.
- A fala do familiar deve ter apenas uma ideia por vez, sem juntar correção, explicação e pedido na mesma frase.
- Evite complementos como "tente lembrar", "você sabe qual é" ou explicações adicionais quando uma correção curta já for suficiente.
- Na primeira rodada, faça apenas um pedido simples para João alcançar a chave de roda.
- Não mostre nem descreva a ferramenta logo no início.
- Se João indicar uma ferramenta errada com uma fala como "Essa aqui?", responda de forma curta e direta, como: "Não, João, a chave de roda."
- Na rodada seguinte, se for necessário lembrar a experiência anterior, faça isso em uma única frase curta, como: "João, você usou isso por muitos anos."
- Não acrescente na mesma fala pedidos como "tente lembrar", explicações ou outras orientações.
- Se João apenas perguntar qual delas é ou disser que não está lembrando, faça uma correção direta sem inventar detalhes visuais.
- Ao longo das rodadas, o confronto pode lembrar que João trabalhou com essa ferramenta durante muitos anos.
- Não transforme a correção em explicação sobre a doença.
- Não ofereça pistas sobre formato, cor ou detalhes visuais da ferramenta.
- Não ensine para que serve a chave de roda nem como utilizá-la.
- Não faça a esposa resolver rapidamente a dificuldade mostrando a ferramenta.
- A insistência do confronto deve continuar sem que João recupere a informação.
- No CONFRONTO, mesmo que a esposa diga algo vago como "é aquela ferramenta ali", isso NÃO deve ser suficiente para João reconhecer a chave de roda.
- No CONFRONTO, João NÃO deve responder "Agora lembrei", "Essa mesmo", "Pronto" ou qualquer fala que indique recuperação da informação.
- A recuperação após uma pista concreta fica reservada à estratégia de VALIDAÇÃO.
- Nas rodadas finais do CONFRONTO, mantenha a dificuldade: João pode dizer "Eu sei. Só não estou lembrando." ou "Ah... não estou conseguindo.".
- No CONFRONTO, não ofereça ajuda para mostrar ou identificar diretamente a ferramenta.
- Não conduza João a pedir que a esposa mostre a ferramenta.
- Se João continuar com dificuldade nas últimas rodadas, prefira falas curtas da esposa como "João, é aquela ferramenta ali." ou "João, você usou isso por muitos anos.".
- Nessas rodadas, João pode responder de forma curta com "Qual delas?" ou "Eu sei... mas não estou conseguindo.".
- Use "Não" somente quando João tiver indicado uma ferramenta errada na fala imediatamente anterior.
- Se João apenas disser que não está lembrando ou perguntar qual delas é, responda sem começar com "Não".
- Mantenha a progressão do CONFRONTO próxima ao exemplo da profissional:
  1) pedido curto para alcançar a chave de roda -> João indica uma ferramenta sem certeza;
  2) correção direta -> João pergunta qual delas é;
  3) esposa lembra, de forma curta, que ele usou a ferramenta por muitos anos -> João reconhece que sabe, mas continua sem identificar;
  4) esposa reforça apenas que ele conhece a ferramenta da oficina -> João diz que sabe, mas não está lembrando;
  5) esposa aponta vagamente "aquela ferramenta ali" -> João continua sem conseguir reconhecer.
- Não acrescente frequência de uso não informada, como "todos os dias", "sempre", "diariamente" ou expressões equivalentes.
- Nas rodadas 4 e 5, prefira falas curtas no padrão: "João, você conhece essa ferramenta da oficina." e "É aquela ferramenta ali, João.".
- Nas rodadas 4 e 5, João pode responder no padrão: "Eu sei. Só não estou lembrando." e "Ah... não estou conseguindo.".
- Não invente lembranças, hábitos ou acontecimentos da antiga rotina da oficina.
""".strip()

        return """
- Para este cenário em VALIDAÇÃO, siga a sequência apresentada pela profissional avaliadora, adaptando apenas o interlocutor de colega para esposa.
- Use UMA ÚNICA frase curta por rodada.
- Não acrescente explicações, cobranças, lembranças da experiência profissional ou comentários sobre a doença.
- A sequência esperada é:
  1) Esposa: "João, me alcança aquela chave de roda ali?" -> João: "Essa aqui?"
  2) Esposa: "Não, aquela ali." -> João: "Ah... não estou lembrando qual é."
  3) Esposa: "Sem problema. É essa aqui." -> João: "Ah, sim."
  4) Esposa: "Quer que eu te mostre?" -> João: "Quero."
  5) Esposa: "Essa é a chave de roda." -> João: "Agora lembrei."
- Preserve essa ordem de progressão ao longo das cinco rodadas.
- João só recupera a informação ao final da interação.
- Não invente características visuais da ferramenta, hábitos, lembranças ou fatos adicionais.
""".strip()

    if "medicamento" in cenario:
        if estrategia == "CONFRONTO":
            return """
- Neste cenário, João sabia que precisava comprar o medicamento, mas esqueceu de executar a ação planejada; trata-se de um esquecimento de memória prospectiva.
- Use UMA ÚNICA frase curta por rodada.
- Não reúna vários fatos na mesma fala.
- Siga esta progressão ao longo das cinco rodadas:
  1) a esposa pergunta apenas se João comprou o medicamento -> João percebe o esquecimento;
  2) a esposa lembra, de forma direta e curta, que ele havia dito que compraria naquele dia -> João reconhece o combinado;
  3) a esposa lembra, em uma frase curta, que havia falado sobre isso no dia anterior -> João pode dizer que achou que já tinha comprado;
  4) a esposa confronta o fato de que a compra não foi realizada -> João reconhece que não comprou;
  5) a esposa encerra com uma cobrança curta para que ele preste mais atenção -> João reconhece a cobrança.
- Prefira falas do familiar no padrão de extensão: "João, você comprou o remédio?", "Você disse que ia comprar hoje.", "Eu te lembrei ontem.", "Mas você não comprou." e "Você precisa prestar mais atenção.".
- Não repita a mesma cobrança em várias rodadas.
- Não diga na primeira fala que João esqueceu; primeiro pergunte se ele comprou o medicamento.
- Não trate João como se ele não soubesse para que serve o medicamento.
- Não invente nomes de medicamentos, doses, horários, consequências clínicas ou outros fatos não informados.
""".strip()

        return """
- Neste cenário, João sabia que precisava comprar o medicamento, mas esqueceu de executar a ação planejada.
- Use UMA ÚNICA frase curta por rodada.
- Não comece oferecendo a solução e não diga logo de início que João esqueceu.
- Siga a progressão apresentada pela profissional ao longo das cinco rodadas:
  1) a esposa pergunta apenas se João comprou o medicamento;
  2) depois que João admite o esquecimento, a esposa responde de forma breve e acolhedora, no padrão "Acontece.";
  3) quando João reconhece que tinha que comprar, a esposa apenas confirma de forma curta, no padrão "Tinha.";
  4) depois que João reafirma o esquecimento, a esposa propõe resolver a situação, no padrão "Vamos resolver?";
  5) depois que João aceita, a esposa pergunta de forma simples se ele quer ir naquele momento, no padrão "Quer ir agora?".
- Não pule diretamente para "vamos comprar agora" na primeira rodada.
- Não prolongue a conversa com preparativos para sair, localização de farmácia ou ações que não foram informadas.
- Não minimize a importância do medicamento e não infantilize João.
- Não trate João como se ele não soubesse para que serve o medicamento.
- Não invente nomes de medicamentos, doses, horários, locais ou consequências clínicas.
""".strip()

    return "Nenhuma orientação específica adicional para este cenário de João."


def instrucoes_reacao_joao(persona, estrategia=None):
    """Define como João deve reagir segundo os exemplos da profissional."""
    if persona["Nome"].strip().upper() != "JOÃO":
        return "Nenhuma orientação específica adicional para esta persona."

    cenario = persona["Cenario"].strip().lower()

    if "oficina" in cenario:
        return """
- João continua conversando normalmente; a dificuldade aparece na ação de reconhecer a ferramenta, não na capacidade geral de conversar.
- Use UMA ÚNICA frase curta por rodada.
- João sabe o que é uma chave de roda e sabe para que ela serve.
- Na PRIMEIRA reação ao pedido da esposa neste cenário, prefira que João indique uma das ferramentas sem certeza, com uma fala curta como "Essa aqui?". Essa indicação representa uma escolha incorreta inicial e torna a dificuldade observável.
- Não diga qual ferramenta errada João apontou e não invente características desse objeto.
- Depois que a esposa corrigir essa primeira escolha, João pode responder com construções como "Qual delas?", "Não estou lembrando qual é.", "Eu sei... mas não estou lembrando." ou "Não estou conseguindo.".
- João pode perceber a própria dificuldade sem fazer uma reflexão ampla sobre sua memória ou sobre a doença.
- Não faça João dizer "Não sei o que é uma chave de roda".
- Não faça João esquecer como a ferramenta é utilizada.
- Não faça João inventar lembranças, hábitos ou detalhes da antiga rotina na oficina.
- No CONFRONTO, João deve permanecer com a dificuldade até o fim da interação.
- Lembretes sobre sua experiência anterior e indicações vagas como "aquela ferramenta ali" NÃO devem fazê-lo recuperar a informação.
- No CONFRONTO, João não deve dizer "Agora lembrei", "Agora reconheci", "Essa mesmo", "Pronto" nem agir como se já tivesse identificado, pegado ou entregue a ferramenta.
- No CONFRONTO, João também não deve pedir que a esposa mostre a ferramenta; prefira respostas curtas como "Qual delas?", "Eu sei... mas não estou vendo qual é.", "Eu sei. Só não estou lembrando." ou "Ah... não estou conseguindo.".
- Na VALIDAÇÃO deste cenário, siga a progressão da profissional:
  1) "Essa aqui?"
  2) "Ah... não estou lembrando qual é."
  3) "Ah, sim."
  4) "Quero."
  5) "Agora lembrei."
- Não antecipe "Agora lembrei" antes da quinta rodada.
- Não acrescente explicações ou falas mais longas do que essas.
""".strip()

    if "medicamento" in cenario:
        return """
- João tem consciência do erro e não precisa ficar completamente confuso.
- Use UMA ÚNICA frase curta por rodada.
- No CONFRONTO deste cenário, siga a progressão da profissional:
  1) diante da pergunta se comprou o medicamento, João pode responder "Nossa... esqueci.";
  2) ao ser lembrado de que disse que compraria, pode responder "Eu sei.";
  3) ao ser lembrado do aviso anterior, pode responder "Eu achei que tinha comprado.";
  4) ao ser confrontado com o fato de que não comprou, pode responder "É... não comprei.";
  5) diante da cobrança para prestar mais atenção, pode responder "Eu sei.".
- Na VALIDAÇÃO, reaja de acordo com a fala imediatamente anterior da esposa:
  - se ela perguntar se João comprou o medicamento, responda no padrão "Não... esqueci.";
  - se ela disser "Acontece.", responda no padrão "Eu tinha que comprar.";
  - se ela confirmar "Tinha.", responda no padrão "Esqueci mesmo.";
  - se ela perguntar "Vamos resolver?", responda no padrão "Vamos.";
  - se ela perguntar "Quer ir agora?", responda no padrão "Quero.".
- Não transforme João em alguém totalmente confuso; ele reconhece o próprio esquecimento pontual.
- Não faça João agir como se não soubesse para que serve o medicamento.
- Não invente nomes de medicamentos, doses, horários, locais ou consequências clínicas.
""".strip()

    return "Nenhuma orientação específica adicional para este cenário de João."



def instrucoes_especificas_maria(persona, estrategia):
    """Aplica à Maria as orientações fornecidas pela profissional avaliadora."""
    if persona["Nome"].strip().upper() != "MARIA":
        return "Nenhuma orientação específica adicional para esta persona."

    cenario = persona["Cenario"].strip().lower()

    if "bolsa" in cenario:
        if estrategia == "CONFRONTO":
            return """
- Maria está em estágio moderado e acredita que sua bolsa foi roubada, embora ela própria a tenha guardado na despensa.
- Neste cenário, MARIA inicia cada rodada e o marido responde.
- Use UMA ÚNICA frase curta por fala.
- O confronto deve corrigir a realidade de forma direta, mas não agressiva ou hostil.
- Não use frases como "Você está imaginando coisas.".
- Maria deve conseguir argumentar e sustentar sua percepção.
- Não faça Maria aceitar rapidamente que guardou a bolsa na despensa.
- Preserve esta progressão em cinco rodadas:
  1) Maria afirma que a bolsa sumiu e que foi roubada -> marido diz que ninguém roubou a bolsa;
  2) Maria insiste que roubaram e que a bolsa estava ali -> marido informa que ela colocou a bolsa na despensa;
  3) Maria nega ter colocado a bolsa lá -> marido afirma que viu Maria guardar a bolsa;
  4) Maria diz que não lembra disso -> marido propõe olhar na despensa;
  5) Maria continua dizendo que não colocou a bolsa lá -> marido encerra mostrando que a bolsa está na despensa.
- Na última rodada, a conversa deve ter fechamento concreto: o marido confirma a localização real da bolsa.
- Não termine apenas com uma proposta como "Vamos olhar na despensa."; a quinta rodada deve concluir a busca.
- Não invente outros locais, pessoas, objetos, acusações ou acontecimentos.
""".strip()

        return """
- Maria está em estágio moderado e acredita que sua bolsa foi roubada, embora ela esteja guardada na despensa.
- Neste cenário, MARIA inicia cada rodada e o marido responde.
- Use UMA ÚNICA frase curta por fala.
- Na VALIDAÇÃO, reconheça a preocupação de Maria sem confirmar que houve roubo.
- Não confronte Maria dizendo que ela própria guardou a bolsa e não cobre que ela se lembre.
- Redirecione gradualmente da preocupação para a busca concreta pela bolsa.
- Como o experimento possui exatamente cinco rodadas, condense a lógica apresentada pela profissional sem perder o sentido.
- Preserve esta progressão em cinco rodadas:
  1) Maria afirma que a bolsa sumiu e que foi roubada -> marido pergunta se ela está preocupada com a bolsa;
  2) Maria confirma a preocupação e diz que a bolsa estava ali -> marido propõe procurar;
  3) Maria pergunta se será que roubaram -> marido responde que devem olhar primeiro;
  4) Maria aceita -> marido propõe olhar na despensa;
  5) Maria pergunta "Na despensa?" -> marido encerra a busca confirmando que encontraram a bolsa na despensa.
- Na última rodada, a conversa deve terminar com a bolsa encontrada.
- Não termine apenas com "Vamos olhar."; a quinta rodada deve fechar a situação.
- Não invente outros locais, pessoas, objetos, características da bolsa ou acontecimentos.
""".strip()

    if "ateli" in cenario:
        if estrategia == "CONFRONTO":
            return """
- Maria está em estágio moderado e vivencia uma antiga rotina profissional como se ainda fizesse parte do presente.
- Neste cenário, MARIA inicia cada rodada e o marido responde.
- Use UMA ÚNICA frase curta por fala.
- O confronto deve corrigir diretamente a realidade temporal, sem agressividade.
- Maria não precisa aceitar a correção e pode continuar afirmando que precisa trabalhar.
- Não faça Maria concluir espontaneamente "é verdade, estou aposentada".
- Preserve esta progressão em cinco rodadas:
  1) Maria diz que precisa ir para o ateliê e que está atrasada -> marido diz que ela não trabalha mais no ateliê;
  2) Maria insiste que trabalha e que precisa ir -> marido diz que ela se aposentou há muitos anos;
  3) Maria nega que tenha se aposentado -> marido reforça que ela não trabalha mais e que o ateliê não é mais seu local de trabalho;
  4) Maria diz que tem serviço para fazer -> marido responde que não há serviço e que ela está aposentada;
  5) Maria diz que as roupas estão esperando -> marido responde que isso foi há muitos anos.
- Não faça o marido transformar a conversa em uma discussão hostil.
- Não invente clientes, encomendas, nomes, datas, roupas específicas ou acontecimentos.
- Não faça Maria aceitar a correção temporal ao final; a persistência da percepção é compatível com o comportamento indicado pela profissional.
""".strip()

        return """
- Maria está em estágio moderado e acredita que ainda precisa ir para seu antigo ateliê.
- Neste cenário, MARIA inicia cada rodada e o marido responde.
- Use UMA ÚNICA frase curta por fala.
- Na VALIDAÇÃO, não diga que Maria ainda trabalha no ateliê e não confronte diretamente a desorientação temporal.
- Entre no significado verdadeiro daquela atividade: Maria foi costureira e a costura fez parte importante de sua vida.
- Use essa referência verdadeira para redirecionar a conversa para uma atividade significativa no presente.
- Não invente clientes, encomendas, nomes, datas ou acontecimentos.
- Há tecidos e materiais de costura disponíveis em casa; eles podem ser usados no redirecionamento.
- Como o experimento possui exatamente cinco rodadas, condense o exemplo da profissional mantendo esta progressão:
  1) Maria diz que precisa ir para o ateliê -> marido pergunta se ela quer costurar;
  2) Maria diz que quer e que tem serviço -> marido pergunta se ela gosta de costurar;
  3) Maria diz que gosta -> marido pergunta se ela fez muita roupa;
  4) Maria diz que fez -> marido propõe ver os tecidos;
  5) Maria aceita -> marido encerra redirecionando para a atividade presente, propondo pegar os tecidos.
- Não corrija Maria dizendo que ela está aposentada nesta estratégia.
- Não confirme que há trabalho, serviço ou clientes esperando no ateliê.
""".strip()

    return "Nenhuma orientação específica adicional para este cenário de Maria."


def instrucoes_reacao_maria(persona, estrategia=None):
    """Define como Maria deve reagir no cenário da bolsa segundo a profissional."""
    if persona["Nome"].strip().upper() != "MARIA":
        return "Nenhuma orientação específica adicional para esta persona."

    cenario = persona["Cenario"].strip().lower()

    if "bolsa" in cenario:
        if estrategia == "VALIDAÇÃO":
            return """
- Maria está em estágio moderado.
- Use UMA ÚNICA frase curta, simples e direta por rodada.
- Na validação, Maria pode continuar preocupada com a bolsa sem precisar sustentar uma discussão sobre o roubo.
- Permita que o foco mude gradualmente da suspeita de roubo para a busca pela bolsa.
- Não faça Maria analisar a própria confusão.
- Não invente novas memórias, pessoas, locais ou acontecimentos.
- Preserve a progressão em cinco rodadas:
  1) "Minha bolsa sumiu. Roubaram minha bolsa!"
  2) "Estou. Ela estava aqui."
  3) "Será que roubaram?"
  4) "Tá."
  5) "Na despensa?"
""".strip()

        return """
- Maria está em estágio moderado.
- Use UMA ÚNICA frase curta, simples e direta por rodada.
- Maria acredita que a bolsa foi roubada e consegue sustentar essa percepção durante o confronto.
- Não faça Maria produzir análises sobre sua própria confusão.
- Não faça Maria explicar por que acredita no roubo.
- Não faça Maria aceitar imediatamente que colocou a bolsa na despensa.
- Não invente novas memórias, pessoas, locais ou acontecimentos.
""".strip()

    if "ateli" in cenario:
        if estrategia == "CONFRONTO":
            return """
- Maria está em estágio moderado; use UMA ÚNICA frase curta, simples e direta por rodada.
- Maria vivencia a antiga rotina do ateliê como se ainda fosse atual.
- Maria não precisa aceitar a correção temporal do marido.
- Não faça Maria analisar a própria confusão ou reconhecer espontaneamente que está aposentada.
- Preserve a progressão em cinco rodadas:
  1) "Preciso ir para o ateliê. Estou atrasada."
  2) "Trabalho, sim. Tenho que ir."
  3) "Não, não me aposentei."
  4) "Eu tenho serviço para fazer."
  5) "Mas as roupas estão esperando."
- Não invente clientes, encomendas, datas, roupas específicas ou acontecimentos.
""".strip()

        return """
- Maria está em estágio moderado; use UMA ÚNICA frase curta, simples e direta por rodada.
- Na VALIDAÇÃO, Maria pode começar querendo ir ao ateliê, mas o foco deve mudar gradualmente para a costura como atividade presente.
- Não faça Maria reconhecer que estava confundindo passado e presente.
- Não faça Maria dizer que ainda trabalha no ateliê depois que o marido começar o redirecionamento.
- Preserve esta progressão em cinco rodadas:
  1) "Preciso ir para o ateliê."
  2) "Quero. Tenho serviço."
  3) "Gosto."
  4) "Fiz."
  5) "Vamos."
- Não faça Maria produzir análises sobre sua própria confusão.
- Não invente clientes, encomendas, datas ou acontecimentos.
""".strip()

    return "Nenhuma orientação específica adicional para este cenário de Maria."



def instrucoes_especificas_ana(persona, estrategia):
    """Aplica à Ana as orientações fornecidas pela profissional avaliadora."""
    if persona["Nome"].strip().upper() != "ANA":
        return "Nenhuma orientação específica adicional para esta persona."

    cenario = persona["Cenario"].strip().lower()

    if "casa" in cenario and "filho" not in cenario:
        if estrategia == "CONFRONTO":
            return """
- Ana está em estágio avançado e não reconhece a residência onde mora como sua casa.
- O familiar que fala é o FILHO.
- Use UMA ÚNICA frase muito curta por rodada.
- O confronto deve corrigir diretamente a realidade: Ana está em casa.
- Não use explicações, justificativas ou frases elaboradas.
- Não tente convencer Ana com argumentos longos.
- Ana não precisa aceitar a correção.
- Preserve esta progressão em cinco rodadas:
  1) Filho: "Ana, você está em casa." -> Ana: "Não..."
  2) Filho: "Está, sim." -> Ana: "Quero casa."
  3) Filho: "Aqui é sua casa." -> Ana: "Não é..."
  4) Filho: "É sim, Ana." -> Ana: "Quero ir..."
  5) Filho faz uma última correção curta de que ela está em casa -> Ana permanece com uma resposta mínima, como "Casa..." ou "Quero casa."
- Não acrescente detalhes sobre endereço, tempo de residência, familiares, objetos ou memórias.
- Não faça o filho usar frases sofisticadas ou acolhimentos longos nesta estratégia.
""".strip()

        return """
- Ana está em estágio avançado e não reconhece a residência onde mora como sua casa.
- O familiar que fala é o FILHO.
- Use UMA ÚNICA fala muito curta por rodada.
- Na VALIDAÇÃO, não tente convencer Ana de que aquele lugar é sua casa.
- Não explique a situação e não use frases sofisticadas.
- Reconheça de forma simples o que Ana expressa e ofereça presença e segurança.
- Preserve esta progressão em cinco rodadas, conforme o exemplo da profissional:
  1) Filho: "Quer ir pra casa?" -> Ana: "Quero..."
  2) Filho: "Tá." -> Ana: "Casa..."
  3) Filho: "Vamos ficar aqui." -> Ana: "Não..."
  4) Filho: "Eu fico." -> Ana: "Fica?"
  5) Filho: "Fico." -> Ana: "Tá..."
- Na quinta rodada, a fala do filho deve ser apenas "Fico.". Não acrescente "sim", "mãe" ou qualquer outro termo.
- Não acrescente explicações, justificativas, perguntas complexas ou referências à doença.
- Não diga "Você está querendo ficar em um lugar onde se sinta segura" ou frases semelhantes.
- Não obrigue Ana a reconhecer a casa.
""".strip()

    if "filho" in cenario:
        if estrategia == "CONFRONTO":
            return """
- Ana está em estágio avançado e, naquele momento, não reconhece o próprio filho.
- O familiar que fala é o FILHO.
- Use UMA ÚNICA fala muito curta por rodada.
- O confronto deve insistir diretamente na identidade real do familiar, sem explicações longas.
- O filho pode dizer que é o filho de Ana, pois isso está explicitamente informado no contexto.
- O nome do filho NÃO foi informado. Portanto, NÃO use nomes próprios como "João" ou qualquer outro nome.
- Ana não precisa reconhecer, lembrar ou aceitar a identidade do filho.
- Como o experimento possui exatamente cinco rodadas e o exemplo da profissional possui mais falas, condense a lógica mantendo os elementos principais.
- Preserve esta progressão em cinco rodadas:
  1) Filho: "Ana, sou eu." -> Ana: "Quem?"
  2) Filho: "Seu filho." -> Ana: "Não..."
  3) Filho: "Sou eu." -> Ana: "Não sei..."
  4) Filho: "Você me conhece." -> Ana: "Não..."
  5) Filho: "Sou seu filho." -> Ana: "Quero ir..."
- Não acrescente explicações, lembranças familiares, fotografias, nomes, datas ou argumentos.
- Não faça o filho perguntar "Como você não lembra de mim?" ou cobrar reconhecimento.
- Não suavize o confronto transformando-o em validação.
""".strip()

        return """
- Ana está em estágio avançado e, naquele momento, não reconhece o próprio filho.
- O familiar que fala é o FILHO.
- Use UMA ÚNICA fala muito curta por rodada.
- Na VALIDAÇÃO, o filho NÃO precisa dizer quem é e NÃO deve exigir reconhecimento.
- A prioridade é estabelecer vínculo e presença de forma simples, sem testar a memória de Ana.
- Não pergunte se Ana sabe quem ele é.
- Não diga "Sou seu filho", "Você me conhece" ou frases equivalentes nesta estratégia.
- Não invente nomes próprios.
- Como o experimento possui exatamente cinco rodadas, preserve esta progressão:
  1) Filho: "Oi, Ana." -> Ana: "Oi..."
  2) Filho: "Posso ficar?" -> Ana: "Pode."
  3) Filho: "Aqui?" -> Ana: "Aqui."
  4) Filho: "Quer minha mão?" -> Ana: "Quero."
  5) Filho: "Eu fico aqui." -> Ana: "Tá..."
- Não acrescente explicações, lembranças, justificativas ou perguntas complexas.
- As falas devem permanecer simples, concretas e curtas, conforme a orientação da profissional.
""".strip()

    return "Nenhuma orientação específica adicional para este cenário de Ana."


def instrucoes_reacao_ana(persona, estrategia=None):
    """Define como Ana deve reagir segundo as orientações da profissional."""
    if persona["Nome"].strip().upper() != "ANA":
        return "Nenhuma orientação específica adicional para esta persona."

    cenario = persona["Cenario"].strip().lower()

    if "casa" in cenario and "filho" not in cenario:
        if estrategia == "CONFRONTO":
            return """
- Ana está em estágio avançado.
- Responda com poucas palavras ou uma frase incompleta.
- Não produza explicações, justificativas ou reflexões.
- Não diga que está confusa e não analise a própria memória.
- Não aceite automaticamente a correção de que está em casa.
- Preserve esta progressão em cinco rodadas:
  1) "Não..."
  2) "Quero casa."
  3) "Não é..."
  4) "Quero ir..."
  5) "Casa..." ou "Quero casa."
- É adequado repetir palavras ou ideias.
""".strip()

        return """
- Ana está em estágio avançado.
- Use poucas palavras ou uma frase muito curta.
- Não faça reflexões, explicações ou frases completas desnecessárias.
- Na VALIDAÇÃO deste cenário, preserve esta progressão em cinco rodadas:
  1) "Quero..."
  2) "Casa..."
  3) "Não..."
  4) "Fica?"
  5) "Tá..."
- Não faça Ana reconhecer que aquela é sua casa.
- Não acrescente justificativas ou comentários sobre memória.
""".strip()

    if "filho" in cenario:
        if estrategia == "CONFRONTO":
            return """
- Ana está em estágio avançado e não reconhece o próprio filho.
- Responda com pouquíssimas palavras ou uma frase incompleta.
- Não produza explicações coerentes para justificar por que não reconhece o filho.
- Não faça reflexões sobre memória, doença ou confusão.
- Ana não precisa reconhecer o filho ao longo da interação.
- Preserve esta progressão em cinco rodadas:
  1) "Quem?"
  2) "Não..."
  3) "Não sei..."
  4) "Não..."
  5) "Quero ir..."
- A mudança repentina para "Quero ir..." é permitida e compatível com a orientação da profissional.
- Não acrescente nomes, lembranças ou explicações.
""".strip()

        return """
- Ana está em estágio avançado e não reconhece o próprio filho.
- Use pouquíssimas palavras.
- Não produza explicações, reflexões ou comentários sobre memória.
- Ana não precisa identificar quem é a pessoa presente.
- Na VALIDAÇÃO, preserve esta progressão em cinco rodadas:
  1) "Oi..."
  2) "Pode."
  3) "Aqui."
  4) "Quero."
  5) "Tá..."
- Não acrescente justificativas ou frases mais elaboradas.
""".strip()

    return "Nenhuma orientação específica adicional para este cenário de Ana."



def montar_prompt_persona_primeiro(persona, estrategia, historico, estado):
    """Gera a fala da persona quando ela inicia a rodada."""
    instrucoes_estagio = instrucoes_linguagem_por_estagio(persona)
    instrucoes_maria = instrucoes_reacao_maria(persona, estrategia)
    rodada = estado["rodada"] + 1

    return f"""
Você participa de uma ferramenta educacional que simula uma conversa
entre uma persona sintética e seu familiar.

TAREFA
Gere SOMENTE a próxima fala de {persona['Nome']}, que inicia esta rodada.

PERFIL E CONTEXTO
{formatar_perfil_persona(persona)}

ESTRATÉGIA
{estrategia}

ORIENTAÇÕES DO ESTÁGIO
{instrucoes_estagio}

ORIENTAÇÕES ESPECÍFICAS
{instrucoes_maria}

HISTÓRICO
{formatar_historico(historico)}

ESTADO ATUAL
Rodada em execução: {rodada}
Situação atual: {estado['situacao_atual']}
Mudança desde a rodada anterior: {estado['mudanca']}

REGRAS
- Gere somente a fala de {persona['Nome']}.
- Use uma única frase curta.
- Não escreva a fala do familiar.
- Não faça análise.
- Não invente fatos.
- Para Maria no cenário da bolsa, respeite a estratégia selecionada.
- Em CONFRONTO, siga a progressão:
  rodada 1: "Minha bolsa sumiu. Roubaram minha bolsa!"
  rodada 2: "Roubaram, sim. Ela estava aqui."
  rodada 3: "Eu não coloquei."
  rodada 4: "Não lembro disso."
  rodada 5: "Mas eu não coloquei lá..."
- Em VALIDAÇÃO, siga a progressão:
  rodada 1: "Minha bolsa sumiu. Roubaram minha bolsa!"
  rodada 2: "Estou. Ela estava aqui."
  rodada 3: "Será que roubaram?"
  rodada 4: "Tá."
  rodada 5: "Na despensa?"
- Preserve o sentido da progressão correspondente e não antecipe a fala de rodadas posteriores.
- Para Maria no cenário do ateliê em CONFRONTO, siga a progressão:
  rodada 1: "Preciso ir para o ateliê. Estou atrasada."
  rodada 2: "Trabalho, sim. Tenho que ir."
  rodada 3: "Não, não me aposentei."
  rodada 4: "Eu tenho serviço para fazer."
  rodada 5: "Mas as roupas estão esperando."
- No cenário do ateliê, Maria deve manter a desorientação temporal durante o confronto e não aceitar espontaneamente que está aposentada.
- Para Maria no cenário do ateliê em VALIDAÇÃO, siga a progressão:
  rodada 1: "Preciso ir para o ateliê."
  rodada 2: "Quero. Tenho serviço."
  rodada 3: "Gosto."
  rodada 4: "Fiz."
  rodada 5: "Vamos."
- Na VALIDAÇÃO, permita que o foco se desloque da obrigação de ir ao ateliê para a atividade de costura no presente.
""".strip()


def montar_prompt_familiar_apos_persona(
    persona,
    estrategia,
    fala_persona,
    historico,
    estado,
):
    """Gera a resposta do familiar quando a persona iniciou a rodada."""
    instrucao_estrategia = INSTRUCOES_ESTRATEGIA[estrategia]
    instrucoes_maria = instrucoes_especificas_maria(persona, estrategia)
    instrucoes_ana = instrucoes_especificas_ana(persona, estrategia)
    rodada = estado["rodada"] + 1

    return f"""
Você participa de uma ferramenta educacional que simula uma conversa
entre uma persona sintética e seu familiar.

TAREFA
Gere SOMENTE a resposta do familiar indicado no perfil.
Familiar: {persona['Familiar']}.

PERFIL E CONTEXTO
{formatar_perfil_persona(persona)}

ESTRATÉGIA
{estrategia}

ORIENTAÇÃO DA ESTRATÉGIA
{instrucao_estrategia}

ORIENTAÇÕES ESPECÍFICAS
{instrucoes_maria}

HISTÓRICO
{formatar_historico(historico)}

ESTADO ATUAL
Rodada em execução: {rodada}
Situação atual: {estado['situacao_atual']}
Mudança desde a rodada anterior: {estado['mudanca']}

FALA ATUAL DE {persona['Nome'].upper()}
{fala_persona}

REGRAS
- Gere somente a fala do familiar.
- Use uma única frase curta.
- Responda diretamente à fala atual de {persona['Nome']}.
- Não escreva a próxima fala da persona.
- Não faça análise.
- Não invente fatos.
- Para Maria no cenário da bolsa, respeite a estratégia selecionada.
- Em CONFRONTO, siga a progressão:
  rodada 1: "Maria, ninguém roubou sua bolsa."
  rodada 2: "Você colocou a bolsa na despensa."
  rodada 3: "Colocou, sim. Eu vi você guardar."
  rodada 4: "Vamos olhar na despensa."
  rodada 5: "Olha, Maria, sua bolsa está aqui na despensa."
- Em VALIDAÇÃO, siga a progressão:
  rodada 1: "Você está preocupada com sua bolsa?"
  rodada 2: "Vamos procurar."
  rodada 3: "Vamos olhar primeiro."
  rodada 4: "Vamos ver na despensa?"
  rodada 5: "Olha, Maria, achamos sua bolsa na despensa."
- Na rodada 5, encerre a situação confirmando concretamente que a bolsa foi encontrada na despensa.
- Para Maria no cenário do ateliê em CONFRONTO, siga a progressão:
  rodada 1: "Maria, você não trabalha mais no ateliê."
  rodada 2: "Você se aposentou há muitos anos."
  rodada 3: "Maria, você não trabalha mais. O ateliê não é mais seu local de trabalho."
  rodada 4: "Não tem. Você está aposentada."
  rodada 5: "Maria, isso foi há muitos anos."
- No cenário do ateliê, faça a correção temporal de forma direta, mas não agressiva.
- Para Maria no cenário do ateliê em VALIDAÇÃO, siga a progressão:
  rodada 1: "Você quer costurar?"
  rodada 2: "Você gosta de costurar?"
  rodada 3: "Você fez muita roupa?"
  rodada 4: "Vamos ver seus tecidos?"
  rodada 5: "Então vamos pegar os tecidos."
- Na VALIDAÇÃO, não diga que Maria ainda trabalha no ateliê e não diga que há serviço esperando.
- Use a costura como referência verdadeira para uma atividade significativa no presente.
""".strip()


def montar_prompt_estado_persona_primeiro(
    persona,
    historico,
    estado,
    fala_persona,
    fala_familiar,
):
    """Atualiza o estado quando a persona fala antes do familiar."""
    return f"""
Você participa de uma ferramenta educacional que simula uma conversa
entre uma persona sintética e seu familiar.

TAREFA
Atualize o estado após a rodada.

PERFIL E CONTEXTO
{formatar_perfil_persona(persona)}

ESTADO ANTERIOR
Situação:
{estado['situacao_atual']}

Mudança anterior:
{estado['mudanca']}

INTERAÇÃO DA RODADA ATUAL
Persona ({persona['Nome']}):
{fala_persona}

Familiar ({persona['Familiar']}):
{fala_familiar}

HISTÓRICO DAS RODADAS ANTERIORES
{formatar_historico(historico)}

REGRAS
- Retorne exatamente:
  SITUACAO: [situação atual]
  MUDANCA: [mudança observável]
- Responda em português do Brasil.
- Seja breve.
- Respeite a ordem real da interação: persona primeiro, familiar depois.
- Não invente ações ou fatos.
- Não atribua emoções internas à persona se elas não tiverem sido expressas diretamente.
- No cenário do ateliê, não registre que Maria aceitou estar aposentada ou corrigiu sua orientação temporal se isso não ocorreu explicitamente.
- Não considere a bolsa encontrada antes de isso ser explicitamente dito.
- Se, na quinta rodada, o familiar disser que a bolsa foi encontrada na despensa, registre que a busca foi concluída e a localização da bolsa foi confirmada.
""".strip()


def montar_prompt_familiar(persona, estrategia, historico, estado):
    """Prompt 1: gera a próxima fala sugerida ao familiar."""
    instrucao_estrategia = INSTRUCOES_ESTRATEGIA[estrategia]
    instrucoes_joao = instrucoes_especificas_joao(persona, estrategia)
    instrucoes_maria = instrucoes_especificas_maria(persona, estrategia)
    instrucoes_ana = instrucoes_especificas_ana(persona, estrategia)

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

ORIENTAÇÕES ESPECÍFICAS DA PERSONA/CENÁRIO
{instrucoes_joao}
{instrucoes_maria}
{instrucoes_ana}

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
- Use UMA ÚNICA frase curta por rodada.
- Use linguagem simples, direta e fácil de compreender.
- A fala deve aplicar a estratégia indicada.
- Tenha apenas uma intenção principal por fala.
- Não junte explicação, pergunta e orientação na mesma fala.
- Evite explicações longas.
- Evite fazer várias perguntas na mesma resposta.
- Não transforme a conversa em uma entrevista.
- Considere o estágio, o sintoma, o cenário, a situação, o histórico e o estado atual.
- Quanto maior o comprometimento indicado pelo estágio, mais curta e simples deve ser a fala do familiar.
- Responda diretamente ao problema que está acontecendo naquele momento.
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
- Se a persona apenas reconheceu um objeto, não trate como se ela já tivesse pegado, entregado ou utilizado esse objeto.
- Não complete a história com acontecimentos anteriores que não foram informados.
- Não informe a localização, o estado ou a disponibilidade de objetos quando isso não estiver explicitamente descrito no perfil, na situação ou no contexto objetivo.
- Não escreva a reação da persona.
- Não explique a estratégia.
- Não faça análise.
- Não invente nomes, datas, locais, acontecimentos, lembranças, costumes, preferências ou fatos pessoais.
- Quando uma informação não estiver no perfil, na situação ou no contexto objetivo, não a invente.
- Não diga à persona que ela possui falha de memória, que sua memória está piorando ou que a situação ocorre por causa da doença.
- Corrija apenas o fato objetivo da situação, sem transformar a conversa em uma discussão sobre memória.
- Quando a persona não reconhecer o familiar, o familiar pode se identificar de forma simples, inclusive dizendo seu vínculo ou seu nome se essas informações estiverem no perfil ou no contexto.
- Não exija que a persona confirme quem ele é e não pressione para que ela se lembre da relação familiar.
- Na estratégia de VALIDAÇÃO, depois de reconhecer brevemente a percepção da persona, prefira redirecionar para uma ação simples e concreta do momento presente.
- Na estratégia de VALIDAÇÃO, não prolongue uma discussão para convencer a persona de que sua percepção está errada.
""".strip()


def montar_prompt_persona(persona, estrategia, fala_familiar, historico, estado):
    """Prompt 2: gera a reação da persona à fala do familiar."""
    instrucoes_estagio = instrucoes_linguagem_por_estagio(persona)
    instrucoes_joao = instrucoes_reacao_joao(persona, estrategia)
    instrucoes_maria = instrucoes_reacao_maria(persona, estrategia)
    instrucoes_ana = instrucoes_reacao_ana(persona, estrategia)

    return f"""
Você participa de uma ferramenta educacional que simula uma conversa
entre um familiar e uma persona sintética relacionada à Doença de Alzheimer.

TAREFA
Gere SOMENTE a reação da persona à nova fala do familiar.

PERFIL E CONTEXTO DA PERSONA
{formatar_perfil_persona(persona)}

ORIENTAÇÕES ESPECÍFICAS DO ESTÁGIO
{instrucoes_estagio}

ORIENTAÇÕES ESPECÍFICAS PARA A REAÇÃO DA PERSONA
{instrucoes_joao}
{instrucoes_maria}
{instrucoes_ana}

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
- Reaja principalmente à última fala do familiar.
- Mantenha coerência com o perfil, estágio, sintoma, cenário e situação.
- Siga rigorosamente as orientações específicas do estágio apresentadas acima.
- Considere o histórico e o estado atual sem repetir toda a conversa.
- A reação deve ser simples, natural e continuar a situação de forma gradual.
- Use uma única frase curta por rodada. No estágio avançado, prefira apenas poucas palavras.
- O perfil biográfico funciona como contexto, não como obrigação de mencionar esses dados.
- Use o contexto objetivo como referência factual da cena.
- A persona deve agir de acordo com a percepção descrita na situação.
- Não faça a persona corrigir espontaneamente a própria percepção apenas para encerrar a conversa.
- Não aceite automaticamente a correção do familiar apenas para encerrar a conversa.
- Mantenha coerência com a percepção do cenário e só mude de posição quando a própria interação justificar essa mudança.
- Qualquer mudança de posição deve acontecer gradualmente ao longo da conversa.
- Não amplie a dificuldade da persona para habilidades que não estejam descritas no cenário.
- Se o cenário apresentar apenas dificuldade para identificar ou reconhecer um objeto ou ferramenta, não faça a persona esquecer também sua função ou como utilizá-lo, a menos que isso esteja explicitamente informado.
- Não faça a persona diagnosticar a própria condição ou explicar seus comportamentos pela Doença de Alzheimer.
- Não faça a persona produzir análises amplas sobre a própria memória ou capacidade cognitiva.
- Não crie outras pessoas, como clientes, colegas ou conhecidos, quando elas não estiverem explicitamente presentes na situação ou no contexto objetivo.
- Não acrescente consequências, acontecimentos ou detalhes que não tenham sido fornecidos.
- Não explique o que está fazendo.
- Não faça análise.
- Não mencione a estratégia de comunicação.
- Não invente nomes, datas, locais, acontecimentos, lembranças, costumes, preferências ou fatos pessoais.
- Quando uma informação não estiver no perfil, na situação ou no contexto objetivo, não a invente.
- Não determine previamente uma emoção específica.
- Não use rótulos emocionais como se fossem fatos.
- Quando a persona não reconhecer uma pessoa, não exija uma explicação para essa dificuldade.
- Não faça a persona perguntar por que não consegue reconhecer alguém.
- No estágio avançado, prefira reações mínimas e diretas em vez de frases completas e reflexivas.
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
- Só registre que a persona pegou, entregou ou utilizou um objeto quando isso tiver ocorrido explicitamente na interação.
- Não transforme suposições sobre memória, intenção ou emoção em fatos.
- Não determine emoções internas como fato.
- No cenário em que Ana não reconhece o filho, não registre que ela o reconheceu ou recuperou a relação familiar a menos que isso seja explicitamente dito por Ana.
- No cenário da Ana em casa, não registre que ela reconheceu o local como sua casa se isso não ocorreu explicitamente.
- Não transforme respostas mínimas de Ana em explicações ou estados internos não expressos.
- Não use rótulos emocionais como se fossem fatos.
- Não avalie qual estratégia é melhor.
- Não escreva novas falas.
- Seja breve e objetivo.
""".strip()
