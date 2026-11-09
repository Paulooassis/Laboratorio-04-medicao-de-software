# Laboratorio-04-medicao-de-software

Testes de hipótese por dentro: comparação entre o **t de Welch** e o **Mann-Whitney** no tempo até o merge de Pull Requests do [langflow](https://github.com/langflow-ai/langflow), com e sem o bot de revisão CodeRabbit.

- Par de testes: [docs/par-de-testes.md](docs/par-de-testes.md)
- Coleta dos dados reais: [docs/coleta-dos-dados.md](docs/coleta-dos-dados.md)
- Cenário, hipóteses e parâmetros da simulação: [docs/cenario-e-hipoteses.md](docs/cenario-e-hipoteses.md)
- Os dois testes aplicados aos dados simulados, com a interpretação: [docs/testes-nos-dados-simulados.md](docs/testes-nos-dados-simulados.md)

## Como rodar

```
pip install -r requirements.txt
python main.py
```

O `main.py` roda tudo do início ao fim, com semente fixa (`numpy.random.default_rng(42)`), então os resultados são sempre os mesmos:

1. **Gera os dados simulados** (`scripts/gerar_dados_simulados.py`): um conjunto para cada cenário (`diferenca_real` e `sem_diferenca`), com 30 PRs por grupo sorteados das distribuições Weibull definidas no cenário. Salva em [`dados/tempo-ate-merge-simulado.csv`](dados/tempo-ate-merge-simulado.csv).
2. **Aplica os dois testes** (`scripts/aplicar_testes.py`): o t de Welch e o Mann-Whitney ao mesmo conjunto de dados de cada cenário, mostrando a estatística, o p-valor, o tamanho do efeito e a decisão sobre H0. Salva em [`resultados/testes-dados-simulados.csv`](resultados/testes-dados-simulados.csv).

### Abrir o dashboard

```
streamlit run dashboard.py
```

Abre o dashboard no navegador, em `http://localhost:8501`. Ele é feito em [Streamlit](https://streamlit.io/), segue as seções da entrega final (Cenário, Os dados, Como os testes funcionam, Erro tipo I, Poder, Dados reais e Conclusão) e mostra no topo os links do repositório e do [GitHub Projects](https://github.com/users/Paulooassis/projects/4).

Dois gráficos já estão prontos, gerados a partir dos CSVs do repositório:

- **G1** (seção *Os dados*): o tempo até o merge dos PRs, com um histograma por grupo, nos dados reais ao lado dos simulados. O eixo é logarítmico porque os tempos vão de segundos a semanas.
- **G2** (seção *Como os testes funcionam*): a distribuição que a estatística de cada teste segue quando H0 é verdadeira, com a região de rejeição (α = 0,05, bilateral) e a área do p-valor de um exemplo.

Os gráficos G3 (erro tipo I) e G4 (poder) entram na Lab04S02.

### Outros scripts

Cada etapa também pode ser rodada sozinha:

| Comando | O que faz |
|---|---|
| `python scripts/gerar_dados_simulados.py` | Só a etapa 1 |
| `python scripts/aplicar_testes.py` | Só a etapa 2, a partir do CSV já gerado |
| `python scripts/coletar_prs.py` | Coleta os dados reais pela API do GitHub e gera `dados/tempo-ate-merge-langflow.csv` |
| `python scripts/parametros_simulacao.py` | Descreve os dados reais e ajusta as distribuições candidatas para a simulação |

#### Simulação de Monte Carlo

A função `run_simulation` (`scripts/simulacao.py`) gera vários conjuntos de dados simulados e aplica o t de Welch e o Mann-Whitney ao mesmo par de amostras em cada repetição, devolvendo os p-valores dos dois testes. Ela não conhece nenhum cenário: para trocar de cenário, basta passar outro gerador ou outros parâmetros. Exemplo, a partir da raiz do repositório:

```python
from scripts.gerar_dados_simulados import gerar_weibull, SEM_BOT, COM_BOT
from scripts.simulacao import run_simulation

p_values = run_simulation(gerar_weibull, SEM_BOT, COM_BOT, n=30, repetitions=10_000, seed=42)
power_welch = (p_values["welch"] < 0.05).mean()
```
