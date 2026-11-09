"""Gera um conjunto de dados simulados do tempo até o merge de PRs, conforme o cenário definido.

Uso: python scripts/gerar_dados_simulados.py [arquivo_de_saida.csv]

Cada grupo segue uma Weibull com a forma e a escala escolhidas a partir dos dados reais
(ver docs/cenario-e-hipoteses.md). São gerados os dois cenários da simulação, com n = 30
por grupo, o mesmo tamanho da amostra real:
  - diferenca_real (H0 falsa): sem_bot ~ Weibull(0,51; 8,2 h) e com_bot ~ Weibull(0,53; 27,2 h)
  - sem_diferenca (H0 verdadeira): os dois grupos ~ Weibull(0,51; 8,2 h)

A semente é fixa (42), então o CSV gerado é sempre o mesmo. As funções deste módulo podem ser
importadas pelos scripts que aplicam os testes e, na Lab04S02, pelas simulações com repetições.
"""
import csv
import sys

import numpy as np
from scipy import stats
from scipy.special import gamma as funcao_gama

SEMENTE = 42
N_POR_GRUPO = 30
SAIDA_PADRAO = "dados/tempo-ate-merge-simulado.csv"
GRUPOS = ["sem_bot", "com_bot"]

# Parâmetros da Weibull (forma k, escala λ em horas), da tabela de docs/cenario-e-hipoteses.md.
SEM_BOT = {"forma": 0.51, "escala": 8.2}
COM_BOT = {"forma": 0.53, "escala": 27.2}

# Outlier situation: the largest real time to merge (com_bot) appears in 1 of every 30 PRs.
OUTLIER_PROB = 1 / 30
OUTLIER_VALUE = 325.7

CENARIOS = {
    "diferenca_real": {"sem_bot": SEM_BOT, "com_bot": COM_BOT},  # H0 falsa: mede o poder
    "sem_diferenca": {"sem_bot": SEM_BOT, "com_bot": SEM_BOT},   # H0 verdadeira: mede o erro tipo I
}


def gerar_weibull(rng, forma, escala, n):
    """Sorteia n tempos (em horas) de uma Weibull com a forma e a escala dadas."""
    return escala * rng.weibull(forma, size=n)


def gerar_weibull_outliers(rng, forma, escala, n, outlier_prob=OUTLIER_PROB, outlier_value=OUTLIER_VALUE):
    """Draw n times (in hours) from a Weibull and replace some of them with an outlier.

    Each value becomes outlier_value with probability outlier_prob. The defaults come from the
    real data: 325.7 h is the largest time to merge observed in the real sample (com_bot group),
    and 1/30 stands for that single case among the 30 PRs of the group. The outliers are injected
    in both groups, so H0 stays true when the two Weibulls are the same.
    """
    x = gerar_weibull(rng, forma, escala, n)
    mask = rng.random(n) < outlier_prob
    x[mask] = outlier_value
    return x


def gerar_cenario(rng, cenario, n=N_POR_GRUPO):
    """Gera um conjunto de dados de um cenário: um array de n tempos por grupo."""
    return {grupo: gerar_weibull(rng, n=n, **CENARIOS[cenario][grupo]) for grupo in GRUPOS}


def mediana_weibull(forma, escala):
    return escala * np.log(2) ** (1 / forma)


def media_weibull(forma, escala):
    return escala * funcao_gama(1 + 1 / forma)


def main():
    saida = sys.argv[1] if len(sys.argv) > 1 else SAIDA_PADRAO
    rng = np.random.default_rng(SEMENTE)

    linhas = []
    for cenario in CENARIOS:
        dados = gerar_cenario(rng, cenario)
        print(f"== {cenario}")
        for grupo in GRUPOS:
            x = dados[grupo]
            params = CENARIOS[cenario][grupo]
            print(f"  {grupo:<8} Weibull(forma {params['forma']}, escala {params['escala']} h) | n={len(x)}"
                  f" | mediana {np.median(x):6.2f} h (teórica {mediana_weibull(**params):6.2f})"
                  f" | média {x.mean():6.2f} h (teórica {media_weibull(**params):6.2f})"
                  f" | máx {x.max():7.2f} h | assimetria {stats.skew(x):.2f}")
            linhas += [{"cenario": cenario, "grupo": grupo, "horas_ate_merge": f"{valor:.4f}"} for valor in x]

    with open(saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=["cenario", "grupo", "horas_ate_merge"])
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"{len(linhas)} observações salvas em {saida} (semente {SEMENTE})")


if __name__ == "__main__":
    main()
