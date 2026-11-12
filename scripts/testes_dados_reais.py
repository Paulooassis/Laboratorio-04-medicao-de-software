"""Aplica o t de Welch e o Mann-Whitney aos dados reais do langflow.

Uso, a partir da raiz do repositório: python scripts/testes_dados_reais.py

Lê dados/tempo-ate-merge-langflow.csv, calcula o tempo até o merge em horas a partir dos horários
exatos (como o dashboard) e aplica os mesmos testes de scripts/aplicar_testes.py. Salva a
estatística, o p-valor, o tamanho do efeito, o IC 95% da diferença de médias e o estimador de
Hodges-Lehmann em resultados/testes-dados-reais.csv.
"""
import csv
import os
from datetime import datetime

import numpy as np

from aplicar_testes import ALFA, formatar, interpretar, teste_mann_whitney, teste_welch

ENTRADA = "dados/tempo-ate-merge-langflow.csv"
SAIDA = "resultados/testes-dados-reais.csv"
FORMATO = "%Y-%m-%dT%H:%M:%SZ"


def ler_dados_reais(entrada=ENTRADA):
    """Tempo até o merge (h) de cada PR real, por grupo."""
    grupos = {}
    with open(entrada, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            delta = datetime.strptime(linha["mergeado_em"], FORMATO) - datetime.strptime(linha["criado_em"], FORMATO)
            grupos.setdefault(linha["grupo"], []).append(delta.total_seconds() / 3600)
    return {grupo: np.array(x) for grupo, x in grupos.items()}


def main():
    grupos = ler_dados_reais()
    sem_bot, com_bot = grupos["sem_bot"], grupos["com_bot"]
    print(f"n = {len(sem_bot)} + {len(com_bot)} | médias: sem_bot {sem_bot.mean():.2f} h, com_bot {com_bot.mean():.2f} h"
          f" | medianas: sem_bot {np.median(sem_bot):.2f} h, com_bot {np.median(com_bot):.2f} h")

    linhas = []
    for resultado in (teste_welch(sem_bot, com_bot), teste_mann_whitney(sem_bot, com_bot)):
        print(f"  {resultado['teste']:<12} {resultado['nome_estatistica']} = {resultado['estatistica']:.3f}"
              f" | p = {resultado['p_valor']:.4f} | {resultado['nome_efeito']} = {resultado['efeito']:.3f}")
        print(f"  {'':<12} {interpretar(resultado)}")
        linhas.append({
            "teste": resultado["teste"],
            "estatistica": formatar(resultado["estatistica"]),
            "gl": formatar(resultado["gl"], 2),
            "p_valor": formatar(resultado["p_valor"], 6),
            "efeito": formatar(resultado["efeito"]),
            "nome_efeito": resultado["nome_efeito"],
            "ic_inferior": formatar(resultado["ic_inferior"]),
            "ic_superior": formatar(resultado["ic_superior"]),
            "hodges_lehmann": formatar(resultado.get("hodges_lehmann")),
            "rejeita_h0": resultado["p_valor"] < ALFA,
        })

    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    with open(SAIDA, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"Resultados salvos em {SAIDA}")


if __name__ == "__main__":
    main()
