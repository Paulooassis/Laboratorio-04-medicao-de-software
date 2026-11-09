"""Measure the type I error of Welch's t-test and Mann-Whitney in the ideal scenario (H0 true).

Usage, from the repository root: python -m scripts.erro_tipo1

Both groups are drawn from the same Weibull (SEM_BOT), so the effect is 0 and every rejection
is a type I error. Both tests are applied to the same 10,000 simulated datasets, and the
rejection rates are saved to resultados/erro_tipo1.csv.
"""
import csv

from scripts.gerar_dados_simulados import SEM_BOT, gerar_weibull
from scripts.simulacao import run_simulation

OUTPUT = "resultados/erro_tipo1.csv"
ALPHA = 0.05
N = 30
REPETITIONS = 10_000
SEED = 42
MARGIN = (0.046, 0.054)  # 5% ± 0.4 p.p.
TESTS = {"welch": "t de Welch", "mann_whitney": "Mann-Whitney"}


def main():
    p_values = run_simulation(gerar_weibull, SEM_BOT, SEM_BOT, n=N, repetitions=REPETITIONS, seed=SEED)

    rows = []
    for key, name in TESTS.items():
        rate = (p_values[key] < ALPHA).mean()
        inside = MARGIN[0] <= rate <= MARGIN[1]
        print(f"{name:<12} rejection rate {rate:.4f} | {'inside' if inside else 'OUTSIDE'} "
              f"the expected margin [{MARGIN[0]}, {MARGIN[1]}]")
        rows.append({"situacao": "ideal", "teste": name, "efeito": 0, "n": N, "taxa_rejeicao": f"{rate:.4f}"})

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["situacao", "teste", "efeito", "n", "taxa_rejeicao"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved to {OUTPUT} ({REPETITIONS} repetitions, seed {SEED})")


if __name__ == "__main__":
    main()
