"""Measure how the power of both tests changes with the sample size (section 6 of the assignment).

Usage, from the repository root: python -m scripts.tamanho_amostra

Part 1 uses the effect observed in the real data: the difference between the medians of the two
Weibull fits of docs/cenario-e-hipoteses.md (about 9.6 h), applied as in scripts/poder.py (only
the scale of group B changes). The power of both tests is measured for several sample sizes, in
the ideal situation and with the outliers of scripts/violacao.py, and the n that reaches 80% of
power is estimated by linear interpolation between the simulated sizes.

Part 2 shows why the p-value alone is not enough with large samples: an increase of 1 h in the
median, about a tenth of the observed effect, is measured with n = 30, 1,000 and 3,000.

The rates are saved to resultados/tamanho_amostra.csv, with the standard columns. They stay out of
resultados/simulacao.csv because they repeat situacao, teste and efeito with different values of n.
"""
import csv

from scripts.gerar_dados_simulados import COM_BOT, SEM_BOT, gerar_weibull, gerar_weibull_outliers, mediana_weibull
from scripts.poder import ALPHA, REPETITIONS, SEED, TESTS
from scripts.simulacao import run_simulation

OUTPUT = "resultados/tamanho_amostra.csv"
SAMPLE_SIZES = [10, 20, 30, 50, 60, 75, 100, 150]
TARGET_POWER = 0.8
SMALL_EFFECT = 1
LARGE_SAMPLES = [30, 1000, 3000]
GENERATORS = {"ideal": gerar_weibull, "violada": gerar_weibull_outliers}


def params_with_effect(effect):
    """Group B parameters with the median `effect` hours above group A, as in scripts/poder.py."""
    base = mediana_weibull(**SEM_BOT)
    return {"forma": SEM_BOT["forma"], "escala": SEM_BOT["escala"] * (base + effect) / base}


def rejection_rates(generator, effect, n):
    p_values = run_simulation(generator, SEM_BOT, params_with_effect(effect), n=n,
                              repetitions=REPETITIONS, seed=SEED)
    return {key: (p_values[key] < ALPHA).mean() for key in TESTS}


def n_for_power(sizes, rates, target=TARGET_POWER):
    """Interpolated n where the power reaches `target`, or None if no simulated size reaches it."""
    if rates[0] >= target:
        return sizes[0]
    for n0, r0, n1, r1 in zip(sizes, rates, sizes[1:], rates[1:]):
        if r0 < target <= r1:
            return n0 + (target - r0) * (n1 - n0) / (r1 - r0)
    return None


def main():
    observed = round(mediana_weibull(**COM_BOT) - mediana_weibull(**SEM_BOT), 2)
    rows = []

    print(f"Part 1: observed effect of {observed} h (difference between the Weibull medians)")
    for situation, generator in GENERATORS.items():
        rates = {key: [] for key in TESTS}
        print(f"  {situation:<8} {'n':>5} | {'t de Welch':>10} | {'Mann-Whitney':>12}")
        for n in SAMPLE_SIZES:
            rate = rejection_rates(generator, observed, n)
            print(f"  {'':<8} {n:>5} | {rate['welch']:>10.4f} | {rate['mann_whitney']:>12.4f}")
            for key, name in TESTS.items():
                rates[key].append(rate[key])
                rows.append({"situacao": situation, "teste": name, "efeito": observed, "n": n,
                             "taxa_rejeicao": f"{rate[key]:.4f}"})
        for key, name in TESTS.items():
            n80 = n_for_power(SAMPLE_SIZES, rates[key])
            reached = f"n ≈ {n80:.0f} per group" if n80 else f"above n = {SAMPLE_SIZES[-1]}"
            print(f"  {situation:<8} {name:<12} reaches {TARGET_POWER:.0%} power at {reached}")

    print(f"\nPart 2: effect of {SMALL_EFFECT} h in the ideal situation, with large samples")
    for n in LARGE_SAMPLES:
        rate = rejection_rates(gerar_weibull, SMALL_EFFECT, n)
        print(f"  n = {n:>5} | t de Welch {rate['welch']:.4f} | Mann-Whitney {rate['mann_whitney']:.4f}")
        for key, name in TESTS.items():
            rows.append({"situacao": "ideal", "teste": name, "efeito": SMALL_EFFECT, "n": n,
                         "taxa_rejeicao": f"{rate[key]:.4f}"})

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["situacao", "teste", "efeito", "n", "taxa_rejeicao"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved to {OUTPUT} ({REPETITIONS} repetitions per combination, seed {SEED})")


if __name__ == "__main__":
    main()
