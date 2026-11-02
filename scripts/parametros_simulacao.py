"""Escolhe a distribuição e os parâmetros da simulação a partir dos dados reais.

Uso: python scripts/parametros_simulacao.py [arquivo.csv]

Lê o CSV gerado por scripts/coletar_prs.py, descreve cada grupo e ajusta (por máxima
verossimilhança, com origem fixa em 0) as distribuições candidatas, comparando-as pelo AIC.
Detalhes e justificativa em docs/cenario-e-hipoteses.md.
"""
import csv
import sys
from datetime import datetime

import numpy as np
from scipy import stats

ENTRADA_PADRAO = "dados/tempo-ate-merge-langflow.csv"
GRUPOS = ["sem_bot", "com_bot"]
CANDIDATAS = {"weibull": stats.weibull_min, "gamma": stats.gamma, "lognormal": stats.lognorm}


def horas_ate_merge(linha):
    # Usa os horários exatos em vez da coluna arredondada, para não haver tempo zero.
    formato = "%Y-%m-%dT%H:%M:%SZ"
    delta = datetime.strptime(linha["mergeado_em"], formato) - datetime.strptime(linha["criado_em"], formato)
    return delta.total_seconds() / 3600


def main():
    entrada = sys.argv[1] if len(sys.argv) > 1 else ENTRADA_PADRAO
    with open(entrada, encoding="utf-8") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    for grupo in GRUPOS:
        x = np.array([horas_ate_merge(l) for l in linhas if l["grupo"] == grupo])
        print(f"== {grupo} (n={len(x)})")
        print(f"  mediana {np.median(x):.2f} h | média {x.mean():.2f} h | desvio-padrão {x.std(ddof=1):.2f} h"
              f" | mín {x.min():.3f} h | máx {x.max():.2f} h")
        print(f"  assimetria {stats.skew(x):.2f} | Shapiro-Wilk p = {stats.shapiro(x).pvalue:.1e}")

        for nome, dist in CANDIDATAS.items():
            params = dist.fit(x, floc=0)
            aic = 2 * 2 - 2 * dist.logpdf(x, *params).sum()  # 2 parâmetros livres (forma e escala)
            forma, escala = params[0], params[-1]
            print(f"  {nome:<10} AIC {aic:6.1f} | forma {forma:.3f} | escala {escala:.2f} h")


if __name__ == "__main__":
    main()
