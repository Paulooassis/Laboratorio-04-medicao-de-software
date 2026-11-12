# Laboratorio-04-medicao-de-software

Testes de hipótese por dentro: comparação entre o **t de Welch** e o **Mann-Whitney** no tempo até o merge de Pull Requests do [langflow](https://github.com/langflow-ai/langflow), com e sem o bot de revisão CodeRabbit.

- Par de testes: [docs/par-de-testes.md](docs/par-de-testes.md)
- Coleta dos dados reais: [docs/coleta-dos-dados.md](docs/coleta-dos-dados.md)
- Cenário, hipóteses e parâmetros da simulação: [docs/cenario-e-hipoteses.md](docs/cenario-e-hipoteses.md)
- Os dois testes aplicados aos dados simulados, com a interpretação: [docs/testes-nos-dados-simulados.md](docs/testes-nos-dados-simulados.md)
- Violação de pressuposto (outliers), expectativa e resultados: [docs/violacao-de-pressuposto.md](docs/violacao-de-pressuposto.md)
- Tamanho da amostra: poder com o efeito observado e n para 80% de poder: [docs/tamanho-da-amostra.md](docs/tamanho-da-amostra.md)
- Nível de significância: erro tipo I e poder com α = 0,05 e α = 0,01: [docs/nivel-de-significancia.md](docs/nivel-de-significancia.md)

## Como rodar

```
pip install -r requirements.txt
python main.py
```

O `main.py` roda tudo do início ao fim e regenera todos os CSV, com semente fixa (`numpy.random.default_rng(42)`), então os resultados são sempre os mesmos. As etapas 3 a 5, 7 e 8 rodam 10.000 repetições por combinação, então **a execução completa leva cerca de 14 minutos**.

1. **Gera os dados simulados** (`scripts/gerar_dados_simulados.py`): um conjunto para cada cenário (`diferenca_real` e `sem_diferenca`), com 30 PRs por grupo sorteados das distribuições Weibull definidas no cenário. Salva em [`dados/tempo-ate-merge-simulado.csv`](dados/tempo-ate-merge-simulado.csv).
2. **Aplica os dois testes** (`scripts/aplicar_testes.py`): o t de Welch e o Mann-Whitney ao mesmo conjunto de dados de cada cenário, mostrando a estatística, o p-valor, o tamanho do efeito e a decisão sobre H0. Salva em [`resultados/testes-dados-simulados.csv`](resultados/testes-dados-simulados.csv).
3. **Mede o erro tipo I no cenário ideal** (`scripts/erro_tipo1.py`): 10.000 repetições com H0 verdadeira. Salva em [`resultados/erro_tipo1.csv`](resultados/erro_tipo1.csv).
4. **Mede o poder no cenário ideal** (`scripts/poder.py`): 10.000 repetições para cada efeito (0, 2, 5, 10, 15 e 20 h). Salva em [`resultados/poder.csv`](resultados/poder.csv).
5. **Repete o erro tipo I e o poder na situação com outliers** (`scripts/violacao.py`): os mesmos efeitos e repetições, com a violação descrita em [docs/violacao-de-pressuposto.md](docs/violacao-de-pressuposto.md). Salva em [`resultados/violacao.csv`](resultados/violacao.csv).
6. **Consolida os resultados da simulação** (`scripts/consolidar_resultados.py`): junta as linhas de `poder.csv` e `violacao.csv`, sem alterar nenhum valor, depois de conferir as colunas, a ausência de combinações repetidas e que `erro_tipo1.csv` é igual ao efeito 0 de `poder.csv`. Salva em [`resultados/simulacao.csv`](resultados/simulacao.csv).
7. **Mede o poder com outros tamanhos de amostra** (`scripts/tamanho_amostra.py`): o efeito observado nos dados reais (cerca de 9,6 h na mediana) com n de 10 a 150, no cenário ideal e com outliers, e um efeito de 1 h com n de até 3.000. A análise está em [docs/tamanho-da-amostra.md](docs/tamanho-da-amostra.md). Salva em [`resultados/tamanho_amostra.csv`](resultados/tamanho_amostra.csv).
8. **Compara α = 0,05 e α = 0,01** (`scripts/alfa.py`): a mesma simulação das etapas 4 e 5, com os mesmos p-valores comparados aos dois níveis. A análise está em [docs/nivel-de-significancia.md](docs/nivel-de-significancia.md). Salva em [`resultados/alfa.csv`](resultados/alfa.csv).

### Abrir o dashboard

```
streamlit run dashboard.py
```

Abre o dashboard no navegador, em `http://localhost:8501`. Ele é feito em [Streamlit](https://streamlit.io/), segue as seções da entrega final (Cenário, Os dados, Como os testes funcionam, Erro tipo I, Poder, Dados reais e Conclusão) e mostra no topo os links do repositório e do [GitHub Projects](https://github.com/users/Paulooassis/projects/4).

Os quatro gráficos são gerados a partir dos CSVs do repositório, sem valores digitados à mão, e cada teste tem sempre a mesma cor:

- **G1** (seção *Os dados*): o tempo até o merge dos PRs, com um histograma por grupo, nos dados reais ao lado dos simulados. O eixo é logarítmico porque os tempos vão de segundos a semanas.
- **G2** (seção *Como os testes funcionam*): a distribuição que a estatística de cada teste segue quando H0 é verdadeira, com a região de rejeição (α = 0,05, bilateral) e a área do p-valor de um exemplo.
- **G3** (seção *Erro tipo I*): a taxa de erro tipo I dos dois testes no cenário ideal e no cenário com outliers, com a linha de referência em 5% e a margem de erro da simulação (±0,4 p.p.). Lê o efeito 0 de `resultados/simulacao.csv`.
- **G4** (seção *Poder*): a taxa de rejeição dos dois testes por tamanho do efeito, uma curva por teste em cada situação. Lê `resultados/simulacao.csv`.

O dashboard só lê os CSV já gravados no repositório, então abre na hora, sem precisar rodar o `main.py` antes.

### Outros scripts

Cada etapa também pode ser rodada sozinha:

| Comando | O que faz |
|---|---|
| `python scripts/gerar_dados_simulados.py` | Só a etapa 1 |
| `python scripts/aplicar_testes.py` | Só a etapa 2, a partir do CSV já gerado |
| `python scripts/coletar_prs.py` | Coleta os dados reais pela API do GitHub e gera `dados/tempo-ate-merge-langflow.csv` |
| `python scripts/parametros_simulacao.py` | Descreve os dados reais e ajusta as distribuições candidatas para a simulação |
| `python -m scripts.erro_tipo1` | Mede o erro tipo I no cenário ideal e gera `resultados/erro_tipo1.csv` |
| `python -m scripts.poder` | Mede o poder no cenário ideal, com efeitos crescentes, e gera `resultados/poder.csv` |
| `python -m scripts.violacao` | Repete o erro tipo I e o poder na situação com outliers e gera `resultados/violacao.csv` |
| `python -m scripts.consolidar_resultados` | Só a etapa 6: junta `poder.csv` e `violacao.csv` em `resultados/simulacao.csv`, a partir dos CSV já gerados |
| `python -m scripts.tamanho_amostra` | Só a etapa 7: mede o poder com outros tamanhos de amostra e gera `resultados/tamanho_amostra.csv` |
| `python -m scripts.alfa` | Só a etapa 8: compara o erro tipo I e o poder com α = 0,05 e α = 0,01 e gera `resultados/alfa.csv` |

#### Simulação de Monte Carlo

A função `run_simulation` (`scripts/simulacao.py`) gera vários conjuntos de dados simulados e aplica o t de Welch e o Mann-Whitney ao mesmo par de amostras em cada repetição, devolvendo os p-valores dos dois testes. Ela não conhece nenhum cenário: para trocar de cenário, basta passar outro gerador ou outros parâmetros. Exemplo, a partir da raiz do repositório:

```python
from scripts.gerar_dados_simulados import gerar_weibull, SEM_BOT, COM_BOT
from scripts.simulacao import run_simulation

p_values = run_simulation(gerar_weibull, SEM_BOT, COM_BOT, n=30, repetitions=10_000, seed=42)
power_welch = (p_values["welch"] < 0.05).mean()
```

## Formato dos resultados

Os gráficos e o dashboard devem ler **apenas [`resultados/simulacao.csv`](resultados/simulacao.csv)**. Ele tem 24 linhas, uma para cada combinação de situação (2), teste (2) e efeito (6), com estas colunas:

| Coluna | Conteúdo |
|---|---|
| `situacao` | `ideal` ou `violada` |
| `teste` | `t de Welch` ou `Mann-Whitney` |
| `efeito` | Aumento da mediana do grupo B, em horas; 0 significa H0 verdadeira (erro tipo I) |
| `n` | Tamanho da amostra de cada grupo |
| `taxa_rejeicao` | Proporção de p-valores < 0,05 nas 10.000 repetições, entre 0 e 1 |

`erro_tipo1.csv`, `poder.csv` e `violacao.csv` são as saídas intermediárias de cada etapa. O efeito 0 de `poder.csv` é o próprio erro tipo I, então `erro_tipo1.csv` não entra no consolidado, para não duplicar essas linhas.

O [`resultados/tamanho_amostra.csv`](resultados/tamanho_amostra.csv) usa as mesmas colunas, mas fica fora do consolidado: ele repete a mesma situação, o mesmo teste e o mesmo efeito com vários valores de `n`, e misturá-lo ao `simulacao.csv` quebraria as curvas do G4, que são uma por situação e teste.

O [`resultados/alfa.csv`](resultados/alfa.csv) também fica fora do consolidado: tem as mesmas colunas mais `alfa` (0,05 ou 0,01), e as linhas com α = 0,05 são iguais às do `simulacao.csv`.

Já o [`resultados/testes-dados-simulados.csv`](resultados/testes-dados-simulados.csv) é a saída da Sprint 1. Ele se refere a **um único conjunto de dados** e guarda a estatística, o p-valor e o tamanho do efeito de cada teste, por isso tem formato próprio.
