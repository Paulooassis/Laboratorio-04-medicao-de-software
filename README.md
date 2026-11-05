# Laboratorio-04-medicao-de-software

Testes de hipótese por dentro: comparação entre o **t de Welch** e o **Mann-Whitney** no tempo até o merge de Pull Requests do [langflow](https://github.com/langflow-ai/langflow), com e sem o bot de revisão CodeRabbit.

- Par de testes: [docs/par-de-testes.md](docs/par-de-testes.md)
- Coleta dos dados reais: [docs/coleta-dos-dados.md](docs/coleta-dos-dados.md)
- Cenário, hipóteses e parâmetros da simulação: [docs/cenario-e-hipoteses.md](docs/cenario-e-hipoteses.md)

## Como rodar

```
pip install -r requirements.txt
```

### Gerar os dados simulados

```
python scripts/gerar_dados_simulados.py
```

Gera um conjunto de dados simulados para cada cenário (`diferenca_real` e `sem_diferenca`), com 30 PRs por grupo sorteados das distribuições Weibull definidas no cenário, e salva em [`dados/tempo-ate-merge-simulado.csv`](dados/tempo-ate-merge-simulado.csv). A semente é fixa (`numpy.random.default_rng(42)`), então o arquivo gerado é sempre o mesmo.

### Outros scripts

| Comando | O que faz |
|---|---|
| `python scripts/coletar_prs.py` | Coleta os dados reais pela API do GitHub e gera `dados/tempo-ate-merge-langflow.csv` |
| `python scripts/parametros_simulacao.py` | Descreve os dados reais e ajusta as distribuições candidatas para a simulação |
