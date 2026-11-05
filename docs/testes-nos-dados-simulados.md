# Os dois testes aplicados aos dados simulados

Os testes foram aplicados ao conjunto de dados simulado em [`dados/tempo-ate-merge-simulado.csv`](../dados/tempo-ate-merge-simulado.csv), gerado com semente fixa (42) a partir das distribuições definidas em [cenario-e-hipoteses.md](cenario-e-hipoteses.md). Em cada cenário, o **t de Welch** e o **Mann-Whitney** foram aplicados ao **mesmo par de amostras** (`sem_bot` e `com_bot`, com 30 PRs cada). Os dois testes são bilaterais, com **α = 0,05**.

Resultados calculados por [`scripts/aplicar_testes.py`](../scripts/aplicar_testes.py) e salvos em [`resultados/testes-dados-simulados.csv`](../resultados/testes-dados-simulados.csv). As diferenças são sempre `com_bot − sem_bot`, ou seja, valores positivos indicam que os PRs com bot demoraram mais.

## Hipóteses

| Teste | H0 | H1 |
|---|---|---|
| t de Welch | μ<sub>sem_bot</sub> = μ<sub>com_bot</sub> | μ<sub>sem_bot</sub> ≠ μ<sub>com_bot</sub> |
| Mann-Whitney | P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) = 0,5 | P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) ≠ 0,5 |

## Cenário "diferença real" (H0 falsa)

Neste cenário, os dados foram gerados com a diferença observada nos dados reais: `sem_bot` ~ Weibull(*k* = 0,51, λ = 8,2 h) e `com_bot` ~ Weibull(*k* = 0,53, λ = 27,2 h). **Sabemos que H0 é falsa nos dois testes**: a diferença verdadeira entre as médias é de 33,3 h, e P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) = 0,65.

| Grupo | Média | Mediana |
|---|---|---|
| `sem_bot` | 12,46 h | 3,75 h |
| `com_bot` | 26,90 h | 4,67 h |

| Teste | Estatística | p-valor | Tamanho do efeito | Decisão (α = 0,05) |
|---|---|---|---|---|
| t de Welch | t = 1,134 (gl = 33,3) | **0,265** | diferença de médias = 14,4 h (IC 95%: −11,5 h a 40,4 h) | não rejeita H0 |
| Mann-Whitney | U = 543 | **0,171** | P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) = 0,60 (Hodges-Lehmann: 2,1 h) | não rejeita H0 |

**Interpretação.** Nas duas amostras, os PRs com bot demoraram mais, em média (+14,4 h) e na comparação par a par: em 60% dos pares, o PR com bot foi o mais lento. Mesmo assim, **nenhum dos dois testes rejeitou H0**. Com p = 0,265, o t de Welch não encontra evidência de que as médias sejam diferentes. O intervalo de confiança da diferença vai de −11,5 h a +40,4 h e inclui o zero. Com p = 0,171, o Mann-Whitney não encontra evidência de que um grupo tenda a ter tempos maiores que o outro.

Como os dados foram gerados por nós, sabemos que **H0 é falsa: os dois testes cometeram um erro tipo II** (não detectaram uma diferença que existe). Isso aconteceu por dois motivos:

- **A amostra sorteada ficou abaixo da diferença verdadeira.** A mediana do `com_bot` saiu em 4,7 h, contra 13,6 h na distribuição de origem, e a diferença de médias saiu em 14,4 h, contra 33,3 h. Com n = 30 e cauda longa, uma amostra pode se afastar bastante da distribuição de onde veio. A semente não foi trocada para conseguir uma amostra mais "favorável".
- **A cauda longa infla a variância.** Um único PR de 371 h no `com_bot` eleva o desvio-padrão e encolhe a estatística t. O Mann-Whitney, que usa só a ordem dos valores, sofre menos com isso e chegou mais perto de rejeitar (p = 0,171 contra 0,265).

O p-valor menor do Mann-Whitney está de acordo com a expectativa do grupo, mas **um único conjunto de dados não permite dizer qual teste é melhor**: com outra semente, o resultado poderia se inverter. Quantas vezes cada teste detecta a diferença é a pergunta Q2 (poder), que será respondida na Lab04S02 com 10.000 repetições.

## Cenário "sem diferença" (H0 verdadeira)

Neste cenário, os dois grupos foram gerados pela mesma distribuição, Weibull(*k* = 0,51, λ = 8,2 h). **Sabemos que H0 é verdadeira nos dois testes.**

| Grupo | Média | Mediana |
|---|---|---|
| `sem_bot` | 18,19 h | 7,11 h |
| `com_bot` | 12,60 h | 4,14 h |

| Teste | Estatística | p-valor | Tamanho do efeito | Decisão (α = 0,05) |
|---|---|---|---|---|
| t de Welch | t = −0,704 (gl = 39,9) | **0,485** | diferença de médias = −5,6 h (IC 95%: −21,6 h a 10,4 h) | não rejeita H0 |
| Mann-Whitney | U = 441 | **0,900** | P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) = 0,49 (Hodges-Lehmann: −0,3 h) | não rejeita H0 |

**Interpretação.** As amostras diferem um pouco por acaso: a média do `sem_bot` saiu 5,6 h maior. Mas **os dois testes não rejeitam H0**, que é a decisão correta. O Mann-Whitney dá p = 0,900, e P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) = 0,49 fica quase exatamente em 0,5. O t de Welch dá p = 0,485, e o intervalo de confiança inclui o zero. Nenhum dos testes cometeu erro tipo I nesta amostra. Com que frequência cada teste acusaria uma diferença que não existe é a pergunta Q1 (erro tipo I), também da Lab04S02.

## Como reproduzir

```
pip install -r requirements.txt
python main.py
```
