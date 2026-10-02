import re
from pathlib import Path

import pandas as pd


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """
    file_path = Path("data/clusters_report.txt")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "clusters_report.txt"

    clusters = []
    pattern = re.compile(r"^\s*(\d+)\s+(\d+)\s+([\d,]+)\s*%\s+(.*)$")
    current = None

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                if current:
                    clusters.append(current)
                current = {
                    "cluster": int(match.group(1)),
                    "cantidad_de_palabras_clave": int(match.group(2)),
                    "porcentaje_de_palabras_clave": float(match.group(3).replace(",", ".")),
                    "words": [match.group(4).strip()],
                }
            elif current and line.strip():
                current["words"].append(line.strip())

    if current:
        clusters.append(current)

    records = []
    for c in clusters:
        full_text = " ".join(c["words"])
        cleaned = " ".join(full_text.split())
        if cleaned.endswith("."):
            cleaned = cleaned[:-1].strip()
        records.append({
            "cluster": c["cluster"],
            "cantidad_de_palabras_clave": c["cantidad_de_palabras_clave"],
            "porcentaje_de_palabras_clave": c["porcentaje_de_palabras_clave"],
            "principales_palabras_clave": cleaned,
        })

    return pd.DataFrame(records)

