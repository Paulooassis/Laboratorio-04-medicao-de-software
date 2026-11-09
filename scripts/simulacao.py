"""Generic Monte Carlo simulation that applies Welch's t-test and Mann-Whitney to simulated data."""
import numpy as np
from scipy import stats


def run_simulation(generator, params_a, params_b, n, repetitions, seed=42):
    """Simulate `repetitions` pairs of samples and return the p-values of both tests.

    Parameters:
        generator: function called as generator(rng, n=n, **params) that returns a numpy array.
        params_a: dict with the generator parameters for group A.
        params_b: dict with the generator parameters for group B.
        n: sample size of each group.
        repetitions: number of simulated datasets.
        seed: seed of the single random generator used in all repetitions.

    Returns:
        dict {"welch": array, "mann_whitney": array}, each with `repetitions` p-values.
    """
    rng = np.random.default_rng(seed)
    welch = np.empty(repetitions)
    mann_whitney = np.empty(repetitions)
    for i in range(repetitions):
        a = generator(rng, n=n, **params_a)
        b = generator(rng, n=n, **params_b)
        welch[i] = stats.ttest_ind(b, a, equal_var=False).pvalue
        mann_whitney[i] = stats.mannwhitneyu(b, a, alternative="two-sided").pvalue
    return {"welch": welch, "mann_whitney": mann_whitney}
