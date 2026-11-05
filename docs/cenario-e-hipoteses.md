# Cenário e hipóteses

Par escolhido: **P1 (t de Welch x Mann-Whitney)**, ver [par-de-testes.md](par-de-testes.md). Dados reais: [coleta-dos-dados.md](coleta-dos-dados.md).

## Pergunta

**A adoção do bot de revisão CodeRabbit mudou o tempo até o merge dos Pull Requests do langflow?**

- **Variável:** tempo entre a abertura e o merge do PR, em horas.
- **Grupos independentes:** `sem_bot` (PRs antes da adoção do bot) e `com_bot` (PRs depois da adoção, revisados pelo bot), com 30 PRs cada.

## Hipóteses

Nível de significância **α = 0,05**, com testes **bilaterais**: a pergunta é se o tempo mudou, em qualquer direção.

| Teste | H0 | H1 |
|---|---|---|
| t de Welch | As médias do tempo até o merge são iguais: μ<sub>sem_bot</sub> = μ<sub>com_bot</sub> | As médias são diferentes: μ<sub>sem_bot</sub> ≠ μ<sub>com_bot</sub> |
| Mann-Whitney | Os dois grupos têm a mesma distribuição: um PR sorteado de cada grupo tem a mesma chance de ser o mais rápido, P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) = 0,5 | Um grupo tende a ter tempos maiores: P(X<sub>sem_bot</sub> < X<sub>com_bot</sub>) ≠ 0,5 |

Os dois testes não testam exatamente a mesma coisa: o t de Welch compara médias, e o Mann-Whitney compara se um grupo tende a ter valores maiores que o outro. Na simulação, os dois grupos têm distribuições de formas praticamente iguais e escalas diferentes, e o grupo `com_bot` é mais lento em toda a distribuição. Nesse caso, quando um H0 é falso o outro também é, e a comparação entre os testes é justa.

## O que os dados reais mostram

Calculado com [`scripts/parametros_simulacao.py`](../scripts/parametros_simulacao.py) sobre os horários exatos de criação e merge.

| Grupo | n | Mediana | Média | Desvio-padrão | Mínimo | Máximo | Assimetria | Shapiro-Wilk |
|---|---|---|---|---|---|---|---|---|
| `sem_bot` | 30 | 3,9 h | 15,1 h | 26,4 h | 17 s | 120,7 h | 2,65 | p = 1,2 × 10⁻⁷ |
| `com_bot` | 30 | 13,6 h | 46,6 h | 72,7 h | 19 s | 325,7 h | 2,35 | p = 6,5 × 10⁻⁷ |

Nos dois grupos, a média é cerca de 3 a 4 vezes a mediana e a assimetria passa de 2. Ou seja, a maioria dos PRs é mergeada em poucas horas, e alguns ficam abertos por dias. O teste de Shapiro-Wilk rejeita a normalidade com folga nos dois grupos. Esse é o cenário em que o pressuposto de normalidade do teste t fica em dúvida, mesmo com n = 30.

## Distribuição escolhida para a simulação

Foram ajustadas três distribuições assimétricas comuns para tempos, por máxima verossimilhança. O critério de comparação foi o AIC: quanto menor, melhor o ajuste.

| Distribuição | AIC `sem_bot` | AIC `com_bot` |
|---|---|---|
| **Weibull** | **196,9** | **269,3** |
| Gamma | 197,4 | 269,4 |
| Lognormal | 202,0 | 273,3 |

Escolhemos a **Weibull**. Ela tem o melhor ajuste nos dois grupos e reproduz a mediana, a média e a cauda dos dados reais. A lognormal, que seria a escolha mais óbvia, exagera a cauda. Os PRs mergeados em menos de 1 minuto (três no `sem_bot`, um no `com_bot`) puxam o desvio do log para cerca de 2,4 a 2,5. Com isso, a média da lognormal ajustada fica em ~70 h no `sem_bot`, contra 15 h observadas.

A Weibull tem dois parâmetros: a **forma** *k* e a **escala** λ. Com *k* < 1, a chance de um PR ser mergeado é maior logo depois da abertura e diminui quanto mais tempo ele fica aberto. Por isso a distribuição tem muitos PRs rápidos e uma cauda longa de PRs esquecidos.

| Grupo | Distribuição | Forma *k* | Escala λ | Mediana (real / Weibull) | Média (real / Weibull) | Percentil 90 (real / Weibull) |
|---|---|---|---|---|---|---|
| `sem_bot` | Weibull | 0,51 | 8,2 h | 3,9 h / 4,0 h | 15,1 h / 15,8 h | 45,2 h / 41,9 h |
| `com_bot` | Weibull | 0,53 | 27,2 h | 13,6 h / 13,6 h | 46,6 h / 48,9 h | 105,5 h / 130,6 h |

As formas dos dois grupos são quase iguais (0,51 e 0,53). Isso mostra que o bot mudou a escala do tempo até o merge, cerca de 3 vezes maior, e não o formato da distribuição.

### Cenários da simulação

| Cenário | `sem_bot` | `com_bot` | Para que serve |
|---|---|---|---|
| **Diferença real** (H0 falsa) | Weibull(*k* = 0,51, λ = 8,2 h) | Weibull(*k* = 0,53, λ = 27,2 h) | Medir o **poder**: com que frequência cada teste detecta a diferença que existe nos dados reais |
| **Sem diferença** (H0 verdadeira) | Weibull(*k* = 0,51, λ = 8,2 h) | Weibull(*k* = 0,51, λ = 8,2 h) | Medir a **taxa de falso positivo**: com que frequência cada teste acusa uma diferença que não existe (o esperado é cerca de 5%) |

Em cada repetição, cada grupo terá **n = 30**, o mesmo tamanho da amostra real.

Os dados simulados são gerados por [`scripts/gerar_dados_simulados.py`](../scripts/gerar_dados_simulados.py), com semente fixa (42), e salvos em [`dados/tempo-ate-merge-simulado.csv`](../dados/tempo-ate-merge-simulado.csv).

## O que esperamos antes de simular

**Esperamos que o Mann-Whitney se saia melhor**, isto é, que tenha mais poder para detectar a diferença no cenário real. Esperamos também que os dois testes mantenham a taxa de falso positivo perto de 5% no cenário sem diferença.

Motivos:

- **A cauda longa infla o desvio-padrão.** Com *k* ≈ 0,5, poucos PRs muito demorados dominam a média e o desvio-padrão de cada amostra. Como o t de Welch divide a diferença de médias por esse desvio, a estatística t tende a ficar pequena mesmo quando a diferença existe.
- **n = 30 não basta para "consertar" a assimetria.** O Teorema Central do Limite faz a média amostral se aproximar da normal, mas, com assimetria acima de 2, essa aproximação é lenta. Por isso, com 30 observações, o teste t ainda pode errar.
- **O Mann-Whitney usa postos.** Ele só considera a ordem dos valores. Um PR de 300 h pesa o mesmo que um de 50 h se os dois forem os maiores, então outliers não atrapalham. E como, nos dados reais, os PRs do `com_bot` tendem a ser mais lentos em toda a distribuição, e não só na média, comparar postos é o mais adequado.

## Como reproduzir

```
pip install -r requirements.txt
python scripts/parametros_simulacao.py
python main.py
```
