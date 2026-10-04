# Sistema de Simulação de Cenários de Alzheimer

Estrutura reorganizada para separar as responsabilidades do sistema sem alterar
a lógica experimental principal.

## Arquivos

- `personas.csv`: dados biográficos, estágio, sintoma, cenário e contexto objetivo.
- `prompts.py`: construção dos três prompts usados em cada rodada.
- `llm.py`: comunicação com o GPT-4.1 por meio da API do OpenRouter.
- `simulacao.py`: controle do menu, rodadas, histórico, estado e registro.
- `logs.txt`: criado automaticamente durante as execuções.
- `.env`: deve conter a variável `OPENROUTER_API_KEY`.

## Fluxo por rodada

Cada rodada possui três requisições sequenciais ao GPT-4.1:

1. geração da resposta sugerida ao familiar;
2. geração da reação da persona;
3. atualização da situação atual e da mudança observada.

A resposta de uma etapa é usada na etapa seguinte. O histórico acumulado é
utilizado nas rodadas posteriores.

## Limite

A simulação possui até 5 rodadas.

Portanto, uma execução completa pode realizar até:

`3 requisições por rodada × 5 rodadas = 15 requisições ao modelo`

## Execução

Instale as dependências:

```bash
pip install openai python-dotenv
```

Crie o arquivo `.env` a partir de `.env.example` e inclua sua chave.

Depois execute:

```bash
python3 simulacao.py
```

## Observação experimental

Os perfis biográficos funcionam como contexto para as personas. Eles não
determinam previamente emoções, reações ou resultados da interação.
