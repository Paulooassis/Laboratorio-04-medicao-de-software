"""Coleta o tempo até o merge de PRs do langflow-ai/langflow, antes e depois da adoção do CodeRabbit.

Uso: python scripts/coletar_prs.py [arquivo_de_saida.csv]

Usa a API de busca do GitHub sem autenticação. Se a variável de ambiente GITHUB_TOKEN
estiver definida, ela é usada para ter um limite de requisições maior.
Detalhes da coleta em docs/coleta-dos-dados.md.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

REPO = "langflow-ai/langflow"
BOT = "coderabbitai[bot]"
POR_GRUPO = 30
SAIDA_PADRAO = "dados/tempo-ate-merge-langflow.csv"

# O CodeRabbit passou a comentar nos PRs em 29/05/2025; esse dia fica fora dos dois grupos.
GRUPOS = [
    ("sem_bot", "2025-05-01..2025-05-28", f"-commenter:{BOT}", "desc"),  # os mais próximos da adoção
    ("com_bot", "2025-05-30..2025-06-30", f"commenter:{BOT}", "asc"),    # os primeiros após a adoção
]


def buscar(consulta, ordem):
    url = "https://api.github.com/search/issues?" + urllib.parse.urlencode(
        {"q": consulta, "sort": "created", "order": ordem, "per_page": 100})
    cabecalhos = {"Accept": "application/vnd.github+json", "User-Agent": "lab04-medicao"}
    if os.environ.get("GITHUB_TOKEN"):
        cabecalhos["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    req = urllib.request.Request(url, headers=cabecalhos)
    for _ in range(6):
        try:
            with urllib.request.urlopen(req) as resposta:
                return json.load(resposta)["items"]
        except urllib.error.HTTPError as erro:
            if erro.code != 403:
                raise
            print("Limite da API atingido, aguardando 30 s...", flush=True)
            time.sleep(30)
    sys.exit("Limite da API persistente; tente de novo mais tarde ou defina GITHUB_TOKEN.")


def horas_entre(inicio, fim):
    formato = "%Y-%m-%dT%H:%M:%SZ"
    delta = datetime.strptime(fim, formato) - datetime.strptime(inicio, formato)
    return round(delta.total_seconds() / 3600, 2)


def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else SAIDA_PADRAO
    linhas = []
    for grupo, janela, filtro_bot, ordem in GRUPOS:
        consulta = (f"repo:{REPO} is:pr is:merged -author:app/dependabot -author:app/renovate "
                    f"created:{janela} {filtro_bot}")
        # PRs abertos por bots ficam de fora: o cenário é sobre PRs de pessoas.
        prs = [pr for pr in buscar(consulta, ordem) if pr["user"]["type"] != "Bot"][:POR_GRUPO]
        for pr in prs:
            mergeado_em = pr["pull_request"]["merged_at"]
            linhas.append({
                "grupo": grupo,
                "pr": pr["number"],
                "autor": pr["user"]["login"],
                "criado_em": pr["created_at"],
                "mergeado_em": mergeado_em,
                "horas_ate_merge": horas_entre(pr["created_at"], mergeado_em),
                "url": pr["html_url"],
            })
        print(f"{grupo}: {len(prs)} PRs")
        time.sleep(8)  # evita o limite secundário da API de busca

    with open(saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"{len(linhas)} linhas gravadas em {saida}")


if __name__ == "__main__":
    main()
