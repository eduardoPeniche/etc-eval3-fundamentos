from __future__ import annotations

from typing import Iterable, Tuple

import pandas as pd


def raw_to_dim_city_and_fact(raw_responses: Iterable[dict]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    dim_city_rows = []
    fact_rows = []

    for item in raw_responses:
        city_name = item["city_name"]
        country = item["country"]
        lat = item["lat"]
        lon = item["lon"]
        data = item["data"]

        dim_city_rows.append(
            {
                "city_name": city_name,
                "country": country,
                "lat": lat,
                "lon": lon,
            }
        )

        # Estructura de /data/2.5/air_pollution/history
        # data["list"] contiene múltiples mediciones históricas
        pollution_list = data.get("list", [])

        for pollution_data in pollution_list:
            dt = pollution_data.get("dt")  # Unix timestamp

            main = pollution_data.get("main", {}) or {}
            components = pollution_data.get("components", {}) or {}

            fact_rows.append(
                {
                    "city_name": city_name,
                    "country": country,
                    "dt": dt,  # Unix timestamp (se convertirá en la DB)
                    "aqi": main.get("aqi"),
                    "co": components.get("co"),
                    "no": components.get("no"),
                    "no2": components.get("no2"),
                    "o3": components.get("o3"),
                    "so2": components.get("so2"),
                    "pm2_5": components.get("pm2_5"),
                    "pm10": components.get("pm10"),
                    "nh3": components.get("nh3"),
                }
            )

    dim_city_df = pd.DataFrame(dim_city_rows).drop_duplicates(
        subset=["city_name", "country"]
    )

    fact_air_pollution_df = pd.DataFrame(fact_rows)

    return dim_city_df, fact_air_pollution_df
