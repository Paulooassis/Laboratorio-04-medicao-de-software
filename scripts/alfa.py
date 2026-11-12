"""Compare the type I error and the power of both tests with alpha = 0.05 and alpha = 0.01.

Usage, from the repository root: python -m scripts.alfa

Same simulation as scripts/poder.py and scripts/violacao.py, with the same effects, n, repetitions
and seed, so the rates with alpha = 0.05 are exactly the ones of resultados/simulacao.csv. The
same p-values are compared with both levels, so the difference between the two rates of a
combination comes only from alpha, not from the random samples.

The rates are saved to resultados/alfa.csv, with the standard columns plus `alfa`. They stay out
of resultados/simulacao.csv because they repeat situacao, teste and efeito with another alpha.
"""
import csv

from scripts.gerar_dados_simulados import SEM_BOT, gerar_weibull, gerar_weibull_outliers, mediana_weibull
from scripts.poder import EFFECTS, N, REPETITIONS, SEED, TESTS
from scripts.simulacao import run_simulation

OUTPUT = "resultados/alfa.csv"
ALPHAS = [0.05, 0.01]
GENERATORS = {"ideal": gerar_weibull, "violada": gerar_weibull_outliers}
COLUMNS = ["situacao", "teste", "efeito", "n", "alfa", "taxa_rejeicao"]


def main():
    base = mediana_weibull(**SEM_BOT)

    rows = []
    print(f"{'situation':<8} {'effect (h)':>10} | " + " | ".join(
        f"{name} α={alpha}" for name in TESTS.values() for alpha in ALPHAS))
    for situation, generator in GENERATORS.items():
        for effect in EFFECTS:
            params_b = {"forma": SEM_BOT["forma"], "escala": SEM_BOT["escala"] * (base + effect) / base}
            p_values = run_simulation(generator, SEM_BOT, params_b, n=N, repetitions=REPETITIONS, seed=SEED)
            rates = {(key, alpha): (p_values[key] < alpha).mean() for key in TESTS for alpha in ALPHAS}
            print(f"{situation:<8} {effect:>10} | " + " | ".join(
                f"{rates[key, alpha]:>{len(name) + 8}.4f}" for key, name in TESTS.items() for alpha in ALPHAS))
            for key, name in TESTS.items():
                for alpha in ALPHAS:
                    rows.append({"situacao": situation, "teste": name, "efeito": effect, "n": N,
                                 "alfa": alpha, "taxa_rejeicao": f"{rates[key, alpha]:.4f}"})

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved to {OUTPUT} ({REPETITIONS} repetitions per combination, seed {SEED})")


if __name__ == "__main__":
    main()
