from collections import defaultdict
import gzip
from pathlib import Path


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """
    file_path = Path("data/data.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    values = defaultdict(list)
    with gzip.open(file_path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t")
                values[parts[0]].append(int(parts[1]))

    return [(letter, max(vals), min(vals)) for letter, vals in sorted(values.items())]
