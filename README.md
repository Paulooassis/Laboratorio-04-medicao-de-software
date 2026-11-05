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

### Outros scripts

Cada etapa também pode ser rodada sozinha:

| Comando | O que faz |
|---|---|
| `python scripts/gerar_dados_simulados.py` | Só a etapa 1 |
| `python scripts/aplicar_testes.py` | Só a etapa 2, a partir do CSV já gerado |
| `python scripts/coletar_prs.py` | Coleta os dados reais pela API do GitHub e gera `dados/tempo-ate-merge-langflow.csv` |
| `python scripts/parametros_simulacao.py` | Descreve os dados reais e ajusta as distribuições candidatas para a simulação |
