import json
from pathlib import Path

import numpy as np
import pandas as pd


def pregunta_01():
    """
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """
    file_path = Path("data/insurance.csv.gz")
    if not file_path.exists():
        file_path = Path(__file__).resolve().parent.parent / "data" / "insurance.csv.gz"
        submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
        submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(file_path)

    orig_qis = ["age", "sex", "bmi", "children", "region"]
    orig_sizes = df.groupby(orig_qis)["age"].transform("size")
    original_k = int(orig_sizes.min())
    original_unique_records = int((orig_sizes == 1).sum())

    age_bins = [18, 30, 40, 50, 65]
    age_labels = ["18-29", "30-39", "40-49", "50-64"]
    df["age_group"] = pd.cut(df["age"], bins=age_bins, labels=age_labels, right=False).astype(str)

    bmi_bins = [-np.inf, 18.5, 25.0, 30.0, np.inf]
    bmi_labels = ["bajo peso", "normal", "sobrepeso", "obesidad"]
    df["bmi_group"] = pd.cut(df["bmi"], bins=bmi_bins, labels=bmi_labels, right=False).astype(str)

    def get_children_group(c):
        if c == 0:
            return "0"
        elif c in [1, 2]:
            return "1-2"
        else:
            return "3+"

    df["children_group"] = df["children"].apply(get_children_group)

    schemes_def = {
        "with_children": ["age_group", "sex", "bmi_group", "children_group", "region"],
        "without_children": ["age_group", "sex", "bmi_group", "region"],
    }

    schemes_report = {}
    published_dfs = {}

    for name, qis in schemes_def.items():
        sizes = df.groupby(qis)["age"].transform("size")
        eq_classes = int(df.groupby(qis).ngroups)
        k_before = int(sizes.min())
        suppressed = int((sizes < 5).sum())
        published_mask = sizes >= 5
        published_records = int(published_mask.sum())

        pub_df = df[published_mask]
        published_dfs[name] = pub_df
        pub_groups = pub_df.groupby(qis)
        published_classes = int(pub_groups.ngroups)

        div = pub_groups["smoker"].nunique()
        no_div_classes = int((div == 1).sum())
        no_div_records = int(pub_groups.filter(lambda g: g["smoker"].nunique() == 1).shape[0])

        schemes_report[name] = {
            "quasi_identifiers": qis,
            "equivalence_classes": eq_classes,
            "k_before_suppression": k_before,
            "suppressed_records": suppressed,
            "published_records": published_records,
            "published_classes": published_classes,
            "classes_without_smoker_diversity": no_div_classes,
            "records_without_smoker_diversity": no_div_records,
        }

    # Selected scheme: the one that suppresses fewer records
    selected_scheme = min(schemes_report, key=lambda s: schemes_report[s]["suppressed_records"])
    selected_pub_df = published_dfs[selected_scheme]

    mean_charges_orig = float(df["charges"].mean())
    mean_charges_pub = float(selected_pub_df["charges"].mean())
    smoker_rate_orig = float((df["smoker"] == "yes").mean())
    smoker_rate_pub = float((selected_pub_df["smoker"] == "yes").mean())

    report = {
        "original_k": original_k,
        "original_unique_records": original_unique_records,
        "schemes": schemes_report,
        "selected_scheme": selected_scheme,
        "mean_charges_original": mean_charges_orig,
        "mean_charges_published": mean_charges_pub,
        "smoker_rate_original": smoker_rate_orig,
        "smoker_rate_published": smoker_rate_pub,
    }

    with open(submission_dir / "privacy_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    pub_cols = schemes_def[selected_scheme] + ["smoker", "charges"]
    selected_pub_df[pub_cols].to_csv(submission_dir / "insurance_published.csv", index=False)

    return report

