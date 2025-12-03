import os
from src.etl.extract import fetch_air_pollution_data
from src.etl.transform import raw_to_dim_city_and_fact
from src.etl.load import load_dim_city, load_fact_air_pollution
from src.utils.db import get_engine, init_db


def run() -> None:
    engine = get_engine()
    init_db(engine)

    # 1) Extract
    raw_responses = fetch_air_pollution_data()
    if not raw_responses:
        print("[INFO] No se obtuvo ningún dato de la API.")
        return

    # 2) Transform
    dim_city_df, fact_air_pollution_df = raw_to_dim_city_and_fact(raw_responses)

    # Guardar y actualizar los DF en archivos CSV en data/processed
    dim_city_df.to_csv("data/processed/dim_city.csv", index=False)
    fact_air_pollution_df.to_csv("data/processed/fact_air_pollution.csv", index=False, mode="a", header=not os.path.exists("data/processed/fact_air_pollution.csv"))

    # 3) Load
    load_dim_city(dim_city_df, engine)
    load_fact_air_pollution(fact_air_pollution_df, engine)

    print("[OK] ETL completado correctamente.")


if __name__ == "__main__":
    run()
