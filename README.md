# Sistema de Simulação de Cenários de Alzheimer

Este repositório apresenta uma ferramenta educacional baseada em Modelos de Linguagem de Grande Porte (LLMs) para simulação de interações envolvendo personas sintéticas relacionadas à Doença de Alzheimer.

O sistema foi desenvolvido como parte de uma pesquisa de mestrado e permite comparar duas estratégias de comunicação, **Confronto** e **Validação**, em cenários previamente definidos.

## Estrutura do experimento

O sistema utiliza três personas sintéticas, representando diferentes estágios da Doença de Alzheimer:

- João — estágio leve;
- Maria — estágio moderado;
- Ana — estágio avançado.

Cada persona possui dois cenários, totalizando seis situações simuladas:

1. Não consegue identificar a chave de roda;
2. Esqueceu de comprar o medicamento;
3. Guardou a bolsa na despensa e acredita que foi roubada;
4. Quer ir para o ateliê onde trabalhou como costureira;
5. Não reconhece a casa onde mora;
6. Não reconhece o próprio filho.

Cada cenário é executado com duas estratégias de comunicação:

- CONFRONTO;
- VALIDAÇÃO.

Assim, o conjunto experimental final é composto por:

`6 cenários × 2 estratégias = 12 simulações`

## Funcionamento

O usuário seleciona:

1. a persona;
2. o cenário;
3. a estratégia de comunicação.

Após essa seleção, a simulação é executada automaticamente.

Cada simulação possui exatamente **5 rodadas**.

Em cada rodada são realizadas três requisições sequenciais ao modelo de linguagem:

1. geração da primeira fala da rodada;
2. geração da resposta do outro participante;
3. atualização do estado da interação.

A ordem das duas primeiras requisições depende do cenário. Em determinados cenários, o familiar inicia a rodada; em outros, a persona sintética inicia a interação.

A saída de uma etapa é utilizada como contexto para a etapa seguinte, enquanto o histórico das rodadas anteriores é mantido para preservar a continuidade da interação.

Cada simulação realiza:

`5 rodadas × 3 requisições = 15 requisições`

Nas 12 execuções definitivas utilizadas na avaliação final:

`12 simulações × 15 requisições = 180 requisições ao modelo`

## Modelo de linguagem

Foi utilizado o modelo:

`openai/gpt-4.1`

O acesso ao modelo é realizado por meio da plataforma OpenRouter.

Parâmetros utilizados:

- Temperature: `0.2`
- Max tokens: `160`

## Arquivos principais

- `personas.csv`: contém os dados das personas, estágios, sintomas, cenários, situações e contextos objetivos.
- `prompts.py`: contém as instruções e os prompts utilizados ao longo das rodadas.
- `llm.py`: realiza a comunicação com o modelo GPT-4.1 por meio da API do OpenRouter.
- `simulacao.py`: controla a seleção da persona, cenário e estratégia, além das rodadas, histórico, estado e registro das interações.
- `teste_llm.py`: utilizado para testes de comunicação com o modelo de linguagem.
- `logs.txt`: arquivo gerado durante as execuções e testes realizados ao longo do desenvolvimento.
- `logs_simulacoes_finais.txt`: contém as 12 simulações definitivas utilizadas no conjunto experimental final.
- `.env.example`: exemplo de configuração da variável utilizada para acesso à API.

## Instalação

Instale as dependências necessárias:

```bash
pip install openai python-dotenv
```

## Configuração

Crie um arquivo `.env` a partir do exemplo fornecido em `.env.example` e informe sua chave da API do OpenRouter:

```env
OPENROUTER_API_KEY=sua_chave_aqui
```

Em seguida, execute:

```bash
python simulacao.py
```

> O arquivo `logs_simulacoes_finais.txt` preserva as 12 simulações definitivas utilizadas na avaliação final. Alguns rótulos registrados nesse arquivo refletem a nomenclatura usada no momento das execuções, mas correspondem aos mesmos seis cenários apresentados acima.
