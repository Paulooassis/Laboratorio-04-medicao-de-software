"""Measure the type I error and the power of both tests in the situation with outliers.

Usage, from the repository root: python -m scripts.violacao

Same simulation as scripts/poder.py, with the same effects, n, repetitions and seed, but each
value is replaced by an outlier of 325.7 h with probability 1/30 (see gerar_weibull_outliers).
The effect is applied to the Weibull part of group B, while the outliers keep the fixed value
of 325.7 h in both groups. So, with outliers, the median rises by approximately the effect, not
exactly. Effect 0 is the type I error and the other effects form the power curve.

The rejection rates are saved to resultados/violacao.csv and printed next to the rates of the
ideal situation, read from resultados/poder.csv.
"""
import csv

from scripts.gerar_dados_simulados import SEM_BOT, gerar_weibull_outliers, mediana_weibull
from scripts.poder import ALPHA, EFFECTS, N, REPETITIONS, SEED, TESTS
from scripts.simulacao import run_simulation

OUTPUT = "resultados/violacao.csv"
IDEAL = "resultados/poder.csv"


def main():
    with open(IDEAL, encoding="utf-8") as file:
        ideal = {(int(row["efeito"]), row["teste"]): float(row["taxa_rejeicao"]) for row in csv.DictReader(file)}

    base = mediana_weibull(**SEM_BOT)

    rows = []
    print(f"{'effect (h)':>10} | {'Welch violated':>14} | {'Welch ideal':>11} | {'MW violated':>11} | {'MW ideal':>8}")
    for effect in EFFECTS:
        params_b = {"forma": SEM_BOT["forma"], "escala": SEM_BOT["escala"] * (base + effect) / base}
        p_values = run_simulation(gerar_weibull_outliers, SEM_BOT, params_b, n=N, repetitions=REPETITIONS, seed=SEED)
        rates = {key: (p_values[key] < ALPHA).mean() for key in TESTS}
        print(f"{effect:>10} | {rates['welch']:>14.4f} | {ideal[effect, TESTS['welch']]:>11.4f}"
              f" | {rates['mann_whitney']:>11.4f} | {ideal[effect, TESTS['mann_whitney']]:>8.4f}")
        for key, name in TESTS.items():
            rows.append({"situacao": "violada", "teste": name, "efeito": effect, "n": N,
                         "taxa_rejeicao": f"{rates[key]:.4f}"})

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["situacao", "teste", "efeito", "n", "taxa_rejeicao"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved to {OUTPUT} ({REPETITIONS} repetitions per effect, seed {SEED})")


if __name__ == "__main__":
    main()
