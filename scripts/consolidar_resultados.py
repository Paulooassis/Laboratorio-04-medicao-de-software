"""Consolidate the simulation results into a single CSV, resultados/simulacao.csv.

Usage, from the repository root: python -m scripts.consolidar_resultados

The rows of resultados/poder.csv (ideal situation) are followed by the rows of
resultados/violacao.csv (situation with outliers), without changing any value. Effect 0 of
poder.csv is the type I error, so resultados/erro_tipo1.csv is only checked against it and is not
copied, to avoid duplicating effect 0. Charts and the dashboard should read only the consolidated
file.
"""
import csv

COLUMNS = ["situacao", "teste", "efeito", "n", "taxa_rejeicao"]
TYPE_I_ERROR = "resultados/erro_tipo1.csv"
INPUTS = ["resultados/poder.csv", "resultados/violacao.csv"]
OUTPUT = "resultados/simulacao.csv"


def read_rows(path):
    """Read a results CSV and check that its columns are exactly COLUMNS."""
    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != COLUMNS:
            raise ValueError(f"{path} has columns {reader.fieldnames}, expected {COLUMNS}")
        return list(reader)


def main():
    power, violation = (read_rows(path) for path in INPUTS)

    type_i_error = read_rows(TYPE_I_ERROR)
    effect_zero = [row for row in power if row["efeito"] == "0"]
    if type_i_error != effect_zero:
        raise ValueError(f"The rows of {TYPE_I_ERROR} differ from the effect 0 rows of {INPUTS[0]}: "
                         f"{type_i_error} != {effect_zero}")

    rows = power + violation
    keys = [(row["situacao"], row["teste"], row["efeito"]) for row in rows]
    repeated = {key for key in keys if keys.count(key) > 1}
    if repeated:
        raise ValueError(f"Repeated combinations of situacao, teste and efeito: {sorted(repeated)}")

    with open(OUTPUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} rows saved to {OUTPUT} ({len(power)} from {INPUTS[0]}, {len(violation)} from {INPUTS[1]})")


if __name__ == "__main__":
    main()
