from collections import Counter
import gzip
from pathlib import Path


def pregunta_04():
    """
    Cuente cuántos registros hay en cada mes, usando la fecha de la tercera
    columna (`date`). Represente el mes como un texto de dos dígitos y retorne
    una lista de tuplas `(mes, cantidad)` ordenada por el mes.

    Ejemplo del formato de la respuesta:

        [("01", 3), ("02", 4), ("03", 2), ...]
    """
    file_path = Path("data/data.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "data.csv.gz"

    counts = Counter()
    with gzip.open(file_path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                month = line.split("\t")[2].split("-")[1]
                counts[month] += 1

    return sorted(counts.items())
