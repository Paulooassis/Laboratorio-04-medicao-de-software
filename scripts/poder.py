"""Measure the power of Welch's t-test and Mann-Whitney in the ideal scenario, with growing effects.

Usage, from the repository root: python -m scripts.poder

The effect is the increase, in hours (the same unit as the data), of the median time to merge
of group B over group A. Only the scale of group B changes, so the shape of the distribution
stays the same and the median rises by exactly the effect. The 10 h effect is close to the
difference seen in the real data (medians of 4.0 h and 13.6 h in the Weibull fits of
docs/cenario-e-hipoteses.md, about 9.6 h). Effect 0 is H0 true, so it matches the type I error.

Both tests are applied to the same 10,000 simulated datasets for each effect, and the rejection
rates are saved to resultados/poder.csv.
"""
import csv

from scripts.gerar_dados_simulados import SEM_BOT, gerar_weibull, mediana_weibull
from scripts.simulacao import run_simulation

OUTPUT = "resultados/poder.csv"
ALPHA = 0.05
N = 30
REPETITIONS = 10_000
SEED = 42
EFFECTS = [0, 2, 5, 10, 15, 20]
TESTS = {"welch": "t de Welch", "mann_whitney": "Mann-Whitney"}


def main():
    base = mediana_weibull(**SEM_BOT)

    rows = []
    print(f"{'effect (h)':>10} | {'t de Welch':>10} | {'Mann-Whitney':>12}")
    for effect in EFFECTS:
        params_b = {"forma": SEM_BOT["forma"], "escala": SEM_BOT["escala"] * (base + effect) / base}
        p_values = run_simulation(gerar_weibull, SEM_BOT, params_b, n=N, repetitions=REPETITIONS, seed=SEED)
        rates = {key: (p_values[key] < ALPHA).mean() for key in TESTS}
        print(f"{effect:>10} | {rates['welch']:>10.4f} | {rates['mann_whitney']:>12.4f}")
        for key, name in TESTS.items():
            rows.append({"situacao": "ideal", "teste": name, "efeito": effect, "n": N,
                         "taxa_rejeicao": f"{rates[key]:.4f}"})

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["situacao", "teste", "efeito", "n", "taxa_rejeicao"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved to {OUTPUT} ({REPETITIONS} repetitions per effect, seed {SEED})")


if __name__ == "__main__":
    main()
