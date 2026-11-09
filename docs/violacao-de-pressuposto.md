# Violação de pressuposto: outliers (Q3)

Esta etapa repete o erro tipo I e as curvas de poder do cenário ideal numa situação que viola os pressupostos do teste paramétrico. Ela corresponde às Issues #20 (definir a violação e a expectativa) e #21 (rodar as simulações).

## Violação escolhida

**Outliers somados à distribuição Weibull.** A assimetria forte já está presente no cenário base (Weibull com *k* ≈ 0,5), então os outliers acrescentam uma violação nova.

Cada PR tem probabilidade de **1/30** de assumir o valor de **325,7 h**, o maior tempo real observado (PR 8327, grupo `com_bot`, em [`dados/tempo-ate-merge-langflow.csv`](../dados/tempo-ate-merge-langflow.csv)). Isso equivale, em média, a um caso extremo por grupo de 30 PRs. O valor é cerca de 40 vezes a escala do grupo `sem_bot` (8,2 h).

Os outliers são injetados nos **dois grupos**, para que H0 continue verdadeira quando as duas Weibull forem iguais. O gerador é a função `gerar_weibull_outliers`, em [`scripts/gerar_dados_simulados.py`](../scripts/gerar_dados_simulados.py).

## Expectativa do grupo

Definida antes de rodar as simulações:

> O t de Welch deve ser o teste mais afetado, porque usa a média e o desvio-padrão, que são muito sensíveis a valores extremos. Esperamos que ele perca poder e que sua taxa de erro tipo I se afaste ainda mais de 5%. O Mann-Whitney usa postos e deve ficar perto de 5%, com perda pequena de poder.

## Como a simulação foi feita

O script [`scripts/violacao.py`](../scripts/violacao.py) usa os mesmos efeitos, o mesmo n, o mesmo número de repetições e a mesma semente de [`scripts/poder.py`](../scripts/poder.py): efeitos de 0, 2, 5, 10, 15 e 20 h, n = 30 por grupo, 10.000 repetições por efeito, semente 42 e α = 0,05 (bilateral). Os dois testes são aplicados aos mesmos conjuntos de dados.

O efeito é aplicado à parte Weibull do grupo B: só a escala muda, e os outliers mantêm o valor fixo de 325,7 h nos dois grupos. Por isso, com outliers, a mediana sobe aproximadamente o valor do efeito, e não exatamente. O efeito 0 é o erro tipo I, e os demais formam a curva de poder.

Os resultados estão em [`resultados/violacao.csv`](../resultados/violacao.csv), com `situacao = violada`. Os do cenário ideal estão em [`resultados/erro_tipo1.csv`](../resultados/erro_tipo1.csv) e [`resultados/poder.csv`](../resultados/poder.csv), com `situacao = ideal` e as mesmas colunas.

## Resultados

Taxa de rejeição de H0 (proporção de p-valores < 0,05):

| Efeito (h) | Welch ideal | Welch violada | Mann-Whitney ideal | Mann-Whitney violada |
|---:|---:|---:|---:|---:|
| 0 | 0,0323 | 0,0302 | 0,0497 | 0,0468 |
| 2 | 0,0810 | 0,0568 | 0,0982 | 0,0930 |
| 5 | 0,2306 | 0,1495 | 0,2635 | 0,2433 |
| 10 | 0,4783 | 0,3121 | 0,5424 | 0,4983 |
| 15 | 0,6530 | 0,4670 | 0,7215 | 0,6836 |
| 20 | 0,7537 | 0,5894 | 0,8331 | 0,7962 |

### Algum teste saiu de 5%?

Com 10.000 repetições, a margem esperada em torno de 5% vai de 4,6% a 5,4%.

- **t de Welch: 3,02%.** Ficou fora da margem e abaixo de 5%, ou seja, o teste é **conservador**. No cenário ideal ele já era conservador (3,23%), e os outliers o afastaram um pouco mais de 5%.
- **Mann-Whitney: 4,68%.** Ficou dentro da margem.

### A vantagem de poder mudou de lado?

**Não.** No cenário ideal, o Mann-Whitney teve mais poder em todos os efeitos, e isso se manteve com outliers. A vantagem dele ficou maior:

| Efeito (h) | Mann-Whitney − Welch, ideal | Mann-Whitney − Welch, violada |
|---:|---:|---:|
| 2 | 1,7 p.p. | 3,6 p.p. |
| 5 | 3,3 p.p. | 9,4 p.p. |
| 10 | 6,4 p.p. | 18,6 p.p. |
| 15 | 6,9 p.p. | 21,7 p.p. |
| 20 | 7,9 p.p. | 20,7 p.p. |

Com outliers, o t de Welch perdeu de 2,4 a 18,6 p.p. de poder em relação ao ideal. O Mann-Whitney perdeu de 0,5 a 4,4 p.p.

### A expectativa se confirmou?

**Sim.**

- O t de Welch foi o teste mais afetado. Ele perdeu bastante poder, e o erro tipo I se afastou ainda mais de 5%, embora pouco (cerca de 0,2 p.p.).
- O Mann-Whitney ficou perto de 5% e perdeu pouco poder.

O desvio do t de Welch continuou conservador, e não liberal. Um outlier que cai num só grupo aumenta a diferença de médias, mas aumenta junto o desvio-padrão, de modo que o |t| raramente fica grande. O Mann-Whitney trata o outlier apenas como o maior posto e quase não é afetado.

## Como reproduzir

```
python -m scripts.violacao
```
