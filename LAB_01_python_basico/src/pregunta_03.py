from collections import defaultdict
import gzip
from pathlib import Path


def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """
    file_path = Path("data/data.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    sums = defaultdict(int)
    with gzip.open(file_path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("\t")
                sums[parts[0]] += int(parts[1])

    return sorted(sums.items())
