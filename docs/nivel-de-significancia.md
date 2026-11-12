# Nível de significância: α = 0,05 × α = 0,01

Esta análise prepara a resposta à pergunta 12 da apresentação: o que muda se o grupo usar α = 0,01 em vez de 0,05? Corresponde à Issue #27.

## O que foi simulado

O script [`scripts/alfa.py`](../scripts/alfa.py) repete a simulação de [`scripts/poder.py`](../scripts/poder.py) e [`scripts/violacao.py`](../scripts/violacao.py), com os mesmos efeitos, n = 30 por grupo, 10.000 repetições e semente 42, e compara **os mesmos p-valores** com os dois níveis. Assim, a diferença entre as duas taxas de uma combinação vem só do α, e não de amostras diferentes. As taxas com α = 0,05 são exatamente as de [`resultados/simulacao.csv`](../resultados/simulacao.csv). Os resultados estão em [`resultados/alfa.csv`](../resultados/alfa.csv).

Com 10.000 repetições, a margem de erro de 95% de cada taxa é ±1,96·√(p(1 − p)/10.000): cerca de ±0,4 p.p. perto de 5% e ±0,2 p.p. perto de 1%. É essa margem que aparece como barra de erro no G3.

## Erro tipo I (efeito 0)

| Situação | Teste | α = 0,05 | α = 0,01 |
|---|---|---:|---:|
| Ideal | t de Welch | 3,2% | 0,2% |
| Ideal | Mann-Whitney | 5,0% | 0,9% |
| Com outliers | t de Welch | 3,0% | 0,1% |
| Com outliers | Mann-Whitney | 4,7% | 0,9% |

O Mann-Whitney fica perto do α escolhido nos dois níveis. O t de Welch, que já era conservador com α = 0,05 por causa da assimetria dos dados, fica ainda mais longe do nominal com α = 0,01: rejeita de 5 a 15 vezes menos do que deveria. Nenhum dos dois passa do α, então trocar o nível não cria falsos positivos.

## Poder

| Situação | Efeito (h) | Welch, α = 0,05 | Welch, α = 0,01 | Mann-Whitney, α = 0,05 | Mann-Whitney, α = 0,01 |
|---|---:|---:|---:|---:|---:|
| Ideal | 2 | 8,1% | 1,0% | 9,8% | 2,9% |
| Ideal | 5 | 23,1% | 4,7% | 26,4% | 10,1% |
| Ideal | 10 | 47,8% | 13,9% | 54,2% | 29,2% |
| Ideal | 15 | 65,3% | 24,1% | 72,2% | 48,2% |
| Ideal | 20 | 75,4% | 32,5% | 83,3% | 62,6% |
| Com outliers | 2 | 5,7% | 0,5% | 9,3% | 2,5% |
| Com outliers | 5 | 15,0% | 2,6% | 24,3% | 8,7% |
| Com outliers | 10 | 31,2% | 9,1% | 49,8% | 25,5% |
| Com outliers | 15 | 46,7% | 16,4% | 68,4% | 42,7% |
| Com outliers | 20 | 58,9% | 23,6% | 79,6% | 56,7% |

## O que concluímos

- **α = 0,01 troca falsos positivos por falsos negativos.** O erro tipo I cai para cerca de 1% ou menos, mas o poder cai muito: com o efeito de 10 h, próximo do observado nos dados reais, o t de Welch passa de 47,8% para 13,9% no cenário ideal, e o Mann-Whitney de 54,2% para 29,2%.
- **A queda é maior no t de Welch.** Ele perde cerca de 70% do poder no efeito de 10 h, e o Mann-Whitney perde cerca de 46%. Com α = 0,01, a vantagem do Mann-Whitney sobre o t de Welch fica ainda maior, nos dois cenários.
- **Com n = 30, α = 0,01 deixaria o estudo quase cego.** Para manter 80% de poder com o nível mais rigoroso seria preciso uma amostra bem maior que a de [tamanho-da-amostra.md](tamanho-da-amostra.md), que já pede cerca de 56 PRs por grupo com α = 0,05.
- **A recomendação de teste não muda:** o Mann-Whitney continua controlando o erro tipo I no nível escolhido e tendo mais poder, com qualquer um dos dois α.
