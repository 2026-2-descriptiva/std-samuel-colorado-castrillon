from pathlib import Path

import numpy as np
import pandas as pd


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una entidad pública recibe peticiones, quejas, reclamos y sugerencias
    (PQRS) por dos canales, la página web y las cartas, y la ley le da 15 días
    hábiles para responder cada una. Su tarea es medir si la entidad cumple
    ese plazo.

    Los archivos `data/historical_requests_web.csv.gz` y
    `data/historical_requests_letter.csv.gz` tienen una fila por solicitud
    recibida entre 2016 y 2021 por cada canal, con su identificador
    (`record_id`), la fecha de entrada (`in_date`), el día de la semana de
    entrada (`day_name`) y la fecha de respuesta (`out_date`). Si `out_date`
    está vacía, la solicitud todavía no ha sido respondida.

    Tenga en cuenta lo siguiente:

    - Algunas solicitudes aparecen repetidas: elimine las filas idénticas
      dentro de cada canal, para contar cada solicitud una sola vez. Las
      filas sin `record_id` son solicitudes válidas.
    - Llame `letter` al canal de las cartas y `web` al de la página web.
    - Los días hábiles de respuesta son los días de lunes a viernes
      posteriores a la fecha de entrada, hasta la fecha de respuesta
      incluida. Por ejemplo, una solicitud que entra un viernes y se responde
      el lunes siguiente tardó 1 día hábil. No considere los festivos.
    - Los días calendario de respuesta son la diferencia entre la fecha de
      respuesta y la de entrada.
    - Una solicitud cumple el plazo si fue respondida en 15 días hábiles o
      menos. Una solicitud pendiente no ha cumplido el plazo.
    - `on_time_rate` es la proporción de solicitudes que cumplen el plazo,
      sobre el total de solicitudes, incluidas las pendientes.
    - Las medianas de días se calculan solamente con las solicitudes
      respondidas.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `channel_summary.csv`, con una fila por canal, en orden alfabético:
       `channel`, `requests`, `answered`, `pending`,
       `median_business_days` y `on_time_rate`.

    2. `yearly_summary.csv`, con una fila por año de entrada y canal,
       ordenada por año y luego por canal: `year`, `channel`, `requests`,
       `pending` y `on_time_rate`.

    3. `entry_day_summary.csv`, con una fila por día de entrada, de lunes a
       domingo, con los dos canales juntos: `day_name`, `requests`,
       `median_calendar_days` y `median_business_days`.

    Observe en el tercer archivo cómo cambia la lectura del tiempo de
    respuesta según se cuenten días calendario o días hábiles.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `channel_summary.csv`:

        channel,requests,answered,pending,median_business_days,on_time_rate
        letter,28138,...
        ...
    """
    data_dir = Path("data")
    if not (data_dir / "historical_requests_web.csv.gz").exists():
        data_dir = Path(__file__).resolve().parent.parent / "data"
        submission_dir = Path(__file__).resolve().parent.parent / "submission"
    else:
        submission_dir = Path("submission")

    submission_dir.mkdir(parents=True, exist_ok=True)

    df_web = pd.read_csv(data_dir / "historical_requests_web.csv.gz").drop_duplicates()
    df_web["channel"] = "web"

    df_letter = pd.read_csv(data_dir / "historical_requests_letter.csv.gz").drop_duplicates()
    df_letter["channel"] = "letter"

    df = pd.concat([df_letter, df_web], ignore_index=True)

    in_dt = pd.to_datetime(df["in_date"])
    out_dt = pd.to_datetime(df["out_date"])

    df["calendar_days"] = (out_dt - in_dt).dt.days
    df["year"] = in_dt.dt.year

    answered_mask = df["out_date"].notna()
    in_answered = in_dt[answered_mask].values.astype("datetime64[D]") + np.timedelta64(1, "D")
    out_answered = out_dt[answered_mask].values.astype("datetime64[D]") + np.timedelta64(1, "D")

    df.loc[answered_mask, "business_days"] = np.busday_count(in_answered, out_answered)
    df["on_time"] = (df["business_days"] <= 15).fillna(False)

    # 1. channel_summary
    ch_rows = []
    for ch in ["letter", "web"]:
        sub = df[df["channel"] == ch]
        reqs = int(len(sub))
        ans = int(sub["out_date"].notna().sum())
        pend = int(sub["out_date"].isna().sum())
        med_bus = float(sub.loc[sub["out_date"].notna(), "business_days"].median())
        on_time = float(sub["on_time"].mean())
        ch_rows.append({
            "channel": ch,
            "requests": reqs,
            "answered": ans,
            "pending": pend,
            "median_business_days": med_bus,
            "on_time_rate": on_time,
        })
    channel_summary = pd.DataFrame(ch_rows)

    # 2. yearly_summary
    yr_rows = []
    for (yr, ch), sub in df.groupby(["year", "channel"]):
        reqs = int(len(sub))
        pend = int(sub["out_date"].isna().sum())
        on_time = float(sub["on_time"].mean())
        yr_rows.append({
            "year": int(yr),
            "channel": ch,
            "requests": reqs,
            "pending": pend,
            "on_time_rate": on_time,
        })
    yearly_summary = (
        pd.DataFrame(yr_rows)
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )

    # 3. entry_day_summary
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_rows = []
    for d in days_order:
        sub = df[df["day_name"] == d]
        reqs = int(len(sub))
        med_cal = float(sub.loc[sub["out_date"].notna(), "calendar_days"].median())
        med_bus = float(sub.loc[sub["out_date"].notna(), "business_days"].median())
        day_rows.append({
            "day_name": d,
            "requests": reqs,
            "median_calendar_days": med_cal,
            "median_business_days": med_bus,
        })
    entry_day_summary = pd.DataFrame(day_rows)

    channel_summary.to_csv(submission_dir / "channel_summary.csv", index=False)
    yearly_summary.to_csv(submission_dir / "yearly_summary.csv", index=False)
    entry_day_summary.to_csv(submission_dir / "entry_day_summary.csv", index=False)

    return channel_summary, yearly_summary, entry_day_summary

