# Par de testes escolhido

## Par e cenário

**P1: t de Welch x Mann-Whitney**

- **Cenário:** tempo até o merge de Pull Requests, comparando PRs com e sem bot de revisão.
- **Coleta:** PRs de um repositório público (via API do GitHub) ou de um dataset pronto, com cerca de 30 observações por grupo.

## Justificativa

O P1 é o par mais equilibrado nos quatro critérios avaliados. Os tempos até o merge são fáceis de coletar e de simular (distribuição lognormal), e violam a normalidade de forma natural, com forte assimetria à direita e outliers (PRs esquecidos por semanas), o que torna relevante comparar o teste paramétrico com o não paramétrico. Por envolver apenas dois grupos independentes, o resultado também é simples de explicar na apresentação oral. O cuidado necessário é escolher um repositório em que a adoção do bot tenha uma data clara, para separar os grupos sem ambiguidade.

## Tabela de comparação

| Par | Cenário | Coletar ~30 por grupo (P2: ~15 execuções) | Simular os dados | Chance realista de violar os pressupostos do teste paramétrico | Explicar na apresentação |
|---|---|---|---|---|---|
| **P1**: t de Welch x Mann-Whitney | Tempo até o merge de PRs, com e sem bot de revisão | **Alta.** A API do GitHub ou um dataset pronto tem centenas de PRs. O cuidado é achar um repositório que separe bem "com bot" e "sem bot" (ex.: antes/depois da adoção). | **Alta.** Duas lognormais com medianas diferentes. | **Muito alta.** Tempo de merge é muito assimétrico à direita, com outliers. | **Alta.** Dois grupos: "o bot reduz o tempo mediano de merge?" |
| **P2**: t pareado x Wilcoxon pareado | Tempo de build antes e depois de ativar o cache | **Média.** São 30 builds na própria máquina, o que leva tempo, e o ruído de outros processos interfere. | **Alta.** Normal mais um deslocamento. | **Média.** Pode haver outlier no build frio e n=15 é pequeno, mas as diferenças costumam ficar perto da normal. | **Alta.** "Quanto o cache economiza por build?" |
| **P3**: ANOVA x Kruskal-Wallis | Tempo de revisão de PRs pequenos, médios e grandes | **Média/Alta.** São ~90 PRs, e é preciso definir os cortes de tamanho e equilibrar os grupos. | **Alta.** Três lognormais. | **Alta.** Assimetria e variâncias desiguais entre os grupos. | **Média.** Com três grupos, entram post-hoc e correção para comparações múltiplas. |
| **P4**: Z para proporção x binomial exato | Taxa de builds com falha frente a uma meta de 5% | **Alta.** A aba Actions já lista as execuções, mas é um grupo só. | **Muito alta.** Bernoulli(p). | **Alta, mas de outro tipo.** Com n=30 e p=0,05, n·p=1,5 e a aproximação normal falha. Não envolve assimetria nem outliers. | **Média.** Exige explicar a aproximação normal da binomial. |
| **P5**: Pearson x Spearman | Tamanho do módulo (LOC) x nº de defeitos | **Muito alta.** O dataset NASA MDP / PROMISE já vem pronto, com centenas de módulos. | **Média.** É preciso gerar pares correlacionados e assimétricos, com excesso de zeros. | **Muito alta.** LOC e defeitos são muito assimétricos, cheios de zeros e com outliers. | **Média/Alta.** É intuitivo, mas exige lembrar que correlação não é causalidade. Não há grupos. |
