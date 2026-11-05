"""Aplica o t de Welch e o Mann-Whitney ao conjunto de dados simulado e interpreta o resultado.

Uso: python scripts/aplicar_testes.py [dados_simulados.csv] [resultados.csv]

Lê o CSV gerado por scripts/gerar_dados_simulados.py e, em cada cenário, aplica os dois testes
(bilaterais, α = 0,05) ao mesmo par de amostras `sem_bot` e `com_bot`. As hipóteses estão em
docs/cenario-e-hipoteses.md, e a interpretação dos resultados em docs/testes-nos-dados-simulados.md.

As diferenças são sempre calculadas como com_bot − sem_bot: valores positivos indicam que os PRs
com bot demoraram mais até o merge.
"""
import csv
import os
import sys

import numpy as np
from scipy import stats

ENTRADA_PADRAO = "dados/tempo-ate-merge-simulado.csv"
SAIDA_PADRAO = "resultados/testes-dados-simulados.csv"
ALFA = 0.05


def teste_welch(sem_bot, com_bot):
    """t de Welch bilateral. H0: as médias dos dois grupos são iguais."""
    resultado = stats.ttest_ind(com_bot, sem_bot, equal_var=False)
    ic = resultado.confidence_interval(confidence_level=1 - ALFA)
    return {
        "teste": "t de Welch",
        "estatistica": resultado.statistic,
        "nome_estatistica": "t",
        "gl": resultado.df,
        "p_valor": resultado.pvalue,
        "efeito": com_bot.mean() - sem_bot.mean(),
        "nome_efeito": "diferença de médias (h)",
        "ic_inferior": ic.low,
        "ic_superior": ic.high,
    }


def teste_mann_whitney(sem_bot, com_bot):
    """Mann-Whitney bilateral. H0: P(X_sem_bot < X_com_bot) = 0,5."""
    resultado = stats.mannwhitneyu(com_bot, sem_bot, alternative="two-sided")
    # U de com_bot conta os pares em que o PR com bot demorou mais; dividido pelo nº de pares,
    # estima P(X_sem_bot < X_com_bot), que é 0,5 sob H0.
    return {
        "teste": "Mann-Whitney",
        "estatistica": resultado.statistic,
        "nome_estatistica": "U",
        "gl": None,
        "p_valor": resultado.pvalue,
        "efeito": resultado.statistic / (len(com_bot) * len(sem_bot)),
        "nome_efeito": "P(X_sem_bot < X_com_bot)",
        "ic_inferior": None,
        "ic_superior": None,
        # Hodges-Lehmann: mediana das diferenças entre todos os pares (com_bot − sem_bot).
        "hodges_lehmann": np.median(np.subtract.outer(com_bot, sem_bot)),
    }


def interpretar(resultado):
    rejeita = resultado["p_valor"] < ALFA
    if resultado["teste"] == "t de Welch":
        h0, h1 = "as médias são iguais", "as médias do tempo até o merge são diferentes"
    else:
        h0, h1 = "P(X_sem_bot < X_com_bot) = 0,5", "um grupo tende a ter tempos maiores que o outro"
    if rejeita:
        return f"p < {ALFA}: rejeita H0 ({h0}); há evidência de que {h1}."
    return f"p >= {ALFA}: não rejeita H0 ({h0}); não há evidência suficiente de que {h1}."


def ler_dados(entrada):
    dados = {}
    with open(entrada, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            dados.setdefault(linha["cenario"], {}).setdefault(linha["grupo"], []).append(float(linha["horas_ate_merge"]))
    return {cenario: {grupo: np.array(x) for grupo, x in grupos.items()} for cenario, grupos in dados.items()}


def formatar(valor, casas=4):
    return "" if valor is None else f"{valor:.{casas}f}"


def main():
    entrada = sys.argv[1] if len(sys.argv) > 1 else ENTRADA_PADRAO
    saida = sys.argv[2] if len(sys.argv) > 2 else SAIDA_PADRAO

    linhas = []
    for cenario, grupos in ler_dados(entrada).items():
        sem_bot, com_bot = grupos["sem_bot"], grupos["com_bot"]
        print(f"== {cenario} (n = {len(sem_bot)} + {len(com_bot)})")
        print(f"  médias: sem_bot {sem_bot.mean():.2f} h, com_bot {com_bot.mean():.2f} h"
              f" | medianas: sem_bot {np.median(sem_bot):.2f} h, com_bot {np.median(com_bot):.2f} h")
        for resultado in (teste_welch(sem_bot, com_bot), teste_mann_whitney(sem_bot, com_bot)):
            detalhe = f", gl = {resultado['gl']:.1f}" if resultado["gl"] is not None else ""
            extra = (f", IC 95% [{resultado['ic_inferior']:.2f}; {resultado['ic_superior']:.2f}]"
                     if resultado["ic_inferior"] is not None
                     else f", Hodges-Lehmann {resultado['hodges_lehmann']:.2f} h")
            print(f"  {resultado['teste']:<12} {resultado['nome_estatistica']} = {resultado['estatistica']:.3f}{detalhe}"
                  f" | p = {resultado['p_valor']:.4f} | {resultado['nome_efeito']} = {resultado['efeito']:.3f}{extra}")
            print(f"  {'':<12} {interpretar(resultado)}")
            linhas.append({
                "cenario": cenario,
                "teste": resultado["teste"],
                "estatistica": formatar(resultado["estatistica"]),
                "gl": formatar(resultado["gl"], 2),
                "p_valor": formatar(resultado["p_valor"], 6),
                "efeito": formatar(resultado["efeito"]),
                "nome_efeito": resultado["nome_efeito"],
                "rejeita_h0": resultado["p_valor"] < ALFA,
            })

    os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
    with open(saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"Resultados salvos em {saida}")


if __name__ == "__main__":
    main()
