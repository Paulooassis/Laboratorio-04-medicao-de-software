# Tamanho da amostra

Esta análise responde às perguntas da seção 6 do enunciado ("Para discutir: tamanho da amostra"). Ela não é obrigatória, mas ajuda nas perguntas 14 e 15 da apresentação. Corresponde à Issue #33.

## O que foi simulado

O script [`scripts/tamanho_amostra.py`](../scripts/tamanho_amostra.py) usa o **efeito observado nos dados reais**: a diferença entre as medianas das duas Weibull ajustadas em [cenario-e-hipoteses.md](cenario-e-hipoteses.md), 13,62 h − 4,00 h = **9,63 h**. O efeito é aplicado como em [`scripts/poder.py`](../scripts/poder.py): só a escala do grupo B muda. Esse efeito é o mesmo das curvas do G4, só que exato, em vez do ponto de 10 h mais próximo.

Para cada tamanho de amostra (10, 20, 30, 50, 60, 75, 100 e 150 PRs por grupo), os dois testes são aplicados aos mesmos 10.000 conjuntos simulados, com semente 42 e α = 0,05 (bilateral). Isso foi feito no cenário ideal e na situação com outliers de [violacao-de-pressuposto.md](violacao-de-pressuposto.md). Os resultados estão em [`resultados/tamanho_amostra.csv`](../resultados/tamanho_amostra.csv).

Com 10.000 repetições, a margem de erro de cada taxa fica em torno de ±0,4 p.p. perto de 5% e de ±0,8 p.p. perto de 80%. Diferenças menores que cerca de 1 p.p. entre os testes não devem ser lidas como vantagem de um deles.

## Qual é o poder com a amostra coletada (n = 30)?

| Situação | t de Welch | Mann-Whitney |
|---|---:|---:|
| Ideal | 46,1% | 52,4% |
| Com outliers | 30,0% | 48,3% |

Com 30 PRs por grupo, **nenhum dos testes chega nem perto dos 80% de poder** normalmente buscados. No cenário ideal, um efeito do tamanho do observado passaria despercebido em cerca de metade das amostras. Com outliers, o t de Welch o perderia em 70% delas.

## Quantas observações dariam 80% de poder?

| n por grupo | Welch, ideal | Mann-Whitney, ideal | Welch, com outliers | Mann-Whitney, com outliers |
|---:|---:|---:|---:|---:|
| 10 | 8,5% | 19,4% | 6,4% | 17,0% |
| 20 | 26,9% | 37,9% | 19,3% | 33,2% |
| 30 | 46,1% | 52,4% | 30,0% | 48,3% |
| 50 | 75,0% | 75,7% | 48,7% | 70,3% |
| 60 | 83,0% | 83,3% | 56,2% | 77,3% |
| 75 | 90,8% | 90,6% | 67,4% | 87,0% |
| 100 | 96,8% | 96,7% | 81,0% | 94,8% |
| 150 | 99,7% | 99,7% | 93,5% | 99,2% |

Interpolando entre os tamanhos simulados, 80% de poder exige:

| Situação | t de Welch | Mann-Whitney |
|---|---:|---:|
| Ideal | n ≈ 56 por grupo | n ≈ 56 por grupo |
| Com outliers | n ≈ 98 por grupo | n ≈ 64 por grupo |

No cenário ideal, seria preciso quase **dobrar** a amostra. Com outliers, o Mann-Whitney precisaria de pouco mais que o dobro, e o t de Welch de mais que o **triplo**.

## Essa coleta seria viável no langflow?

**Sim, em volume.** Na coleta real, os 30 PRs sem bot foram criados em 6,3 dias (4,7 PRs por dia) e os 30 com bot em 4,1 dias (7,3 PRs por dia). Nesse ritmo:

- 56 PRs por grupo cobririam cerca de 12 dias antes da adoção do bot e 8 dias depois;
- 98 PRs por grupo cobririam cerca de 21 dias antes e 14 dias depois.

As janelas de busca de [`scripts/coletar_prs.py`](../scripts/coletar_prs.py) (01/05 a 28/05 e 30/05 a 30/06/2025) já cobrem esses períodos. Há dois cuidados:

- **O script lê só a primeira página da busca** (100 resultados) antes de tirar os PRs abertos por bots. Para chegar a ~100 PRs humanos por grupo, ele precisaria paginar.
- **Janelas maiores enfraquecem o desenho antes × depois.** Quanto mais longe da data de adoção, mais chance de outras mudanças no projeto (releases, equipe, volume de PRs) explicarem a diferença em vez do bot. Não há grupo de controle para separar esses efeitos.

## O tamanho da amostra muda qual teste é melhor?

**Sim, no cenário ideal.** A vantagem do Mann-Whitney existe só em amostras pequenas: com n = 10 ele tem mais que o dobro do poder do t de Welch (19,4% contra 8,5%), e com n = 30 ainda está 6,4 p.p. à frente. A partir de **n = 50, os dois empatam** (diferenças abaixo de 1 p.p., dentro da margem de erro). É o Teorema Central do Limite em ação: com a assimetria da Weibull (*k* ≈ 0,5), a média amostral demora para se aproximar da normal, mas com 50 PRs por grupo ela já se comporta bem o bastante para o t de Welch.

**Não, com outliers.** O Mann-Whitney fica à frente em todos os tamanhos simulados, e a diferença chega a 21 p.p. com n = 50 e n = 60. Ela só diminui quando os dois testes se aproximam de 100%. Os outliers não somem com amostras maiores: cada PR continua tendo 1/30 de chance de ser um caso extremo, então eles continuam inflando o desvio-padrão que o t de Welch usa.

Em resumo, **a assimetria pesa mais em amostras pequenas, e os outliers pesam em qualquer tamanho de amostra realista** para este cenário.

## Nos dados reais: o resultado não significativo mostra que não há efeito?

Aplicando os dois testes aos 60 PRs reais com as funções de [`scripts/aplicar_testes.py`](../scripts/aplicar_testes.py), **eles discordam**:

| Teste | Estatística | p-valor | Tamanho do efeito |
|---|---|---:|---|
| t de Welch | t = 2,23 (gl = 36,5) | 0,032 | diferença de médias = 31,5 h (IC 95%: 2,8 h a 60,1 h) |
| Mann-Whitney | U = 579 | 0,058 | P(X<sub>sem bot</sub> < X<sub>com bot</sub>) = 0,64 (Hodges-Lehmann: 3,3 h) |

A tabela oficial dos dados reais, com a interpretação, fica na seção 6 do dashboard (Issue #28).

O Mann-Whitney não rejeitou H0, mas isso **não mostra que não há efeito**. Com n = 30 e um efeito do tamanho do observado, ele rejeita em só 52% das amostras: um resultado não significativo era quase tão provável quanto um significativo, mesmo com o efeito existindo. Ausência de evidência não é evidência de ausência. Com 56 PRs por grupo, a chance de detectar esse efeito subiria para 80%.

O resultado significativo do t de Welch também merece cuidado. Com poder de 46%, as amostras em que o teste rejeita tendem a ser justamente as que exageram a diferença. O intervalo de confiança da diferença de médias, de 2,8 h a 60,1 h, mostra o quanto essa estimativa é imprecisa com 30 PRs por grupo.

## Com amostras muito grandes: p-valor ou tamanho do efeito?

A segunda parte do script simula um efeito de **1 h** na mediana, cerca de um décimo do observado, no cenário ideal:

| n por grupo | t de Welch | Mann-Whitney |
|---:|---:|---:|
| 30 | 4,8% | 6,2% |
| 1.000 | 63,4% | 58,6% |
| 3.000 | 97,8% | 96,6% |

Com 30 PRs, esse efeito é indistinguível de H0 verdadeira: as taxas ficam perto de 5%. Com 3.000 PRs por grupo, os dois testes o declaram "significativo" em quase todas as amostras. O p-valor só diz se a diferença é distinguível do acaso com aquela amostra, e com amostra suficiente quase qualquer diferença é. **Se uma hora a mais na mediana importa num processo em que um PR em cada dez fica aberto por mais de 40 h, quem decide é o contexto, não o p-valor.**

Por isso, com amostras grandes, o que importa é o **tamanho do efeito com seu intervalo de confiança**: a diferença de medianas ou de médias em horas, o Hodges-Lehmann, P(X<sub>sem bot</sub> < X<sub>com bot</sub>). Também chama atenção que, com n grande e efeito pequeno, o t de Welch passa à frente do Mann-Whitney (63,4% contra 58,6% com n = 1.000), confirmando que a desvantagem dele é um problema de amostras pequenas.

## Como reproduzir

```
python -m scripts.tamanho_amostra
```

Leva cerca de 6 minutos. A etapa também roda dentro de `python main.py` (etapa 7).
