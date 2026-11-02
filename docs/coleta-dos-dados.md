# Coleta dos dados reais

Amostra real para o par **P1 (t de Welch x Mann-Whitney)**: tempo até o merge de Pull Requests, com e sem bot de revisão.

- **Arquivo:** [`dados/tempo-ate-merge-langflow.csv`](../dados/tempo-ate-merge-langflow.csv)
- **Observações:** 60 PRs, sendo 30 por grupo
- **Data da coleta:** 01/11/2026

## Origem

- **Repositório:** [langflow-ai/langflow](https://github.com/langflow-ai/langflow), um projeto open-source com alto volume de PRs.
- **Bot de revisão:** [CodeRabbit](https://github.com/apps/coderabbitai) (`coderabbitai[bot]`), que comenta e revisa PRs automaticamente.
- **Adoção do bot:** pelos PRs do repositório, o CodeRabbit passou a comentar nos PRs em **29/05/2025**. Antes dessa data, nenhum PR criado tem comentário dele; depois, quase todos têm.

## Forma de coleta

Os PRs foram obtidos pela [API de busca do GitHub](https://docs.github.com/rest/search/search#search-issues-and-pull-requests) (`GET /search/issues`), sem autenticação, com o script [`scripts/coletar_prs.py`](../scripts/coletar_prs.py). Ele usa só a biblioteca padrão do Python e gera o CSV:

```
python scripts/coletar_prs.py
```

Se a API recusar por limite de requisições, o script espera e tenta de novo. Definir a variável de ambiente `GITHUB_TOKEN` aumenta esse limite. As mesmas buscas também podem ser feitas na interface do GitHub.

| Grupo | Busca | Ordenação | Seleção |
|---|---|---|---|
| `sem_bot` (antes da adoção) | `repo:langflow-ai/langflow is:pr is:merged -author:app/dependabot -author:app/renovate created:2025-05-01..2025-05-28 -commenter:coderabbitai[bot]` | criação, decrescente | os 30 PRs criados mais perto da adoção |
| `com_bot` (depois da adoção) | `repo:langflow-ai/langflow is:pr is:merged -author:app/dependabot -author:app/renovate created:2025-05-30..2025-06-30 commenter:coderabbitai[bot]` | criação, crescente | os 30 primeiros PRs após a adoção |

Critérios aplicados:

- Apenas PRs **mergeados**. PRs fechados sem merge não têm tempo até o merge.
- PRs abertos por bots (`github-actions[bot]`, `coderabbitai[bot]`, `codeflash-ai[bot]`, Dependabot, Renovate) foram excluídos, porque o cenário é sobre PRs de pessoas.
- O dia da transição (29/05/2025) ficou de fora dos dois grupos. O grupo `sem_bot` só tem PRs sem nenhum comentário do bot: três deles (#8237, #8256 e #8259) foram mergeados logo após a adoção, mas o bot não chegou a comentar neles.
- Os grupos ficaram em períodos vizinhos (`sem_bot`: PRs criados de 22/05 a 28/05/2025; `com_bot`: de 30/05 a 03/06/2025), para reduzir o efeito de outras mudanças no projeto ao longo do tempo.

## Colunas do CSV

| Coluna | Descrição |
|---|---|
| `grupo` | `sem_bot` ou `com_bot` |
| `pr` | número do PR no repositório |
| `autor` | login de quem abriu o PR |
| `criado_em` | data e hora de abertura do PR (UTC) |
| `mergeado_em` | data e hora do merge (UTC) |
| `horas_ate_merge` | `mergeado_em - criado_em`, em horas, com duas casas decimais |
| `url` | link do PR |

## Limitações

- O desenho é **antes x depois** da adoção, e não um experimento controlado. Outras mudanças no projeto na mesma época, como releases, mudanças na equipe ou nas regras de revisão, também podem afetar o tempo até o merge.
- O tempo é contado desde a abertura do PR, incluindo o período em que ele ficou como rascunho (*draft*).
- A seleção pega os PRs mais próximos da data de adoção, e não uma amostra aleatória do período.
