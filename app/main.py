import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.utils.db import get_engine
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


st.set_page_config(
    page_title="Calidad del Aire en nuestras ciudades",
    layout="wide",
)

st.title("Calidad del Aire en nuestras ciudades")
st.markdown("Dashboard interactivo para monitorear la contaminación del aire")


@st.cache_data(ttl=300)
def cargar_datos() -> pd.DataFrame:
    """
    Lee los datos de contaminación del aire de la base de datos
    """
    engine = get_engine()
    query = """
        SELECT
            p.dt,
            c.city_name,
            c.country,
            p.aqi,
            p.co,
            p.no,
            p.no2,
            p.o3,
            p.so2,
            p.pm2_5,
            p.pm10,
            p.nh3
        FROM fact_air_pollution p
        JOIN dim_city c ON p.city_id = c.city_id
        ORDER BY p.dt;
    """
    df = pd.read_sql(query, engine)

    # Convertir dt (Unix timestamp) a datetime
    if "dt" in df.columns:
        df["dt"] = pd.to_datetime(df["dt"], unit="s", utc=True, errors="coerce")
        df["fecha"] = df["dt"].dt.date
        df["hora"] = df["dt"].dt.hour

    # Función para obtener descripción del AQI
    def get_aqi_description(aqi):
        if aqi == 1:
            return "Buena"
        elif aqi == 2:
            return "Aceptable"
        elif aqi == 3:
            return "Moderada"
        elif aqi == 4:
            return "Mala"
        elif aqi == 5:
            return "Muy mala"
        else:
            return "Desconocida"

    df["aqi_descripcion"] = df["aqi"].apply(get_aqi_description)

    return df


def get_aqi_color(aqi):
    """Retorna color basado en AQI"""
    if aqi == 1:
        return "green"
    elif aqi == 2:
        return "yellow"
    elif aqi == 3:
        return "orange"
    elif aqi == 4:
        return "red"
    elif aqi == 5:
        return "purple"
    else:
        return "gray"


df = cargar_datos()

if df.empty:
    st.info(
        "Aún no hay datos en la base de datos.\n\n"
        "Ejecuta primero el ETL con:\n\n"
        "`python -m src.etl.pipeline`"
    )
else:
    # --- Filtros ---
    col_filters1, col_filters2 = st.columns(2)

    with col_filters1:
        ciudades = sorted(df["city_name"].unique())
        ciudad_sel = st.selectbox("Selecciona una ciudad", ciudades)

    with col_filters2:
        fechas_disponibles = sorted(df["fecha"].unique())
        fecha_sel = st.selectbox("Selecciona una fecha", fechas_disponibles)

    # Filtrar datos
    df_filtrado = df[(df["city_name"] == ciudad_sel) & (df["fecha"] == fecha_sel)].copy()
    df_filtrado = df_filtrado.sort_values("dt")

    if df_filtrado.empty:
        st.warning("No hay datos disponibles para los filtros seleccionados.")
    else:
        st.subheader(f"Datos de calidad del aire - {ciudad_sel} ({fecha_sel})")

        # --- Métricas principales ---
        ultimo = df_filtrado.iloc[-1]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Índice de Calidad del Aire (AQI)",
                f"{ultimo['aqi']}" if pd.notnull(ultimo['aqi']) else "N/D",
                delta=ultimo['aqi_descripcion']
            )

        with col2:
            st.metric(
                "PM2.5 (μg/m³)",
                f"{ultimo['pm2_5']:.1f}" if pd.notnull(ultimo['pm2_5']) else "N/D",
            )

        with col3:
            st.metric(
                "PM10 (μg/m³)",
                f"{ultimo['pm10']:.1f}" if pd.notnull(ultimo['pm10']) else "N/D",
            )

        with col4:
            st.metric(
                "NO₂ (μg/m³)",
                f"{ultimo['no2']:.1f}" if pd.notnull(ultimo['no2']) else "N/D",
            )

        st.markdown("---")

        # --- Gráfico 1: Evolución del AQI durante el día ---
        st.subheader("Evolución del Índice de Calidad del Aire (AQI)")

        fig_aqi = px.line(
            df_filtrado,
            x="dt",
            y="aqi",
            title=f"AQI a lo largo del día - {ciudad_sel}",
            labels={"dt": "Hora", "aqi": "Índice de Calidad del Aire"},
            color_discrete_sequence=["red"]
        )
        fig_aqi.update_layout(
            xaxis_title="Hora del día",
            yaxis_title="AQI",
            yaxis=dict(tickmode='linear', tick0=1, dtick=1)
        )
        st.plotly_chart(fig_aqi, use_container_width=True)

        # --- Gráfico 2: Comparación de contaminantes ---
        st.subheader("Comparación de concentraciones de contaminantes")

        # Seleccionar contaminante
        contaminantes = ["co", "no", "no2", "o3", "so2", "pm2_5", "pm10", "nh3"]
        nombres_contaminantes = {
            "co": "CO (Monóxido de carbono)",
            "no": "NO (Monóxido de nitrógeno)",
            "no2": "NO₂ (Dióxido de nitrógeno)",
            "o3": "O₃ (Ozono)",
            "so2": "SO₂ (Dióxido de azufre)",
            "pm2_5": "PM2.5 (Partículas finas)",
            "pm10": "PM10 (Partículas gruesas)",
            "nh3": "NH₃ (Amoníaco)"
        }

        contaminante_sel = st.selectbox(
            "Selecciona contaminante para comparar",
            contaminantes,
            format_func=lambda x: nombres_contaminantes[x]
        )

        fig_contaminantes = px.bar(
            df_filtrado,
            x="hora",
            y=contaminante_sel,
            title=f"Concentración de {nombres_contaminantes[contaminante_sel]} por hora",
            labels={"hora": "Hora del día", contaminante_sel: f"Concentración (μg/m³)"},
            color=contaminante_sel,
            color_continuous_scale="Reds"
        )
        st.plotly_chart(fig_contaminantes, use_container_width=True)

        # --- Gráfico 3: Tabla de datos detallados ---
        st.subheader("Datos detallados")

        with st.expander("Ver tabla completa de mediciones"):
            # Formatear la tabla para mejor visualización
            df_tabla = df_filtrado.copy()
            df_tabla["dt"] = df_tabla["dt"].dt.strftime("%H:%M")
            df_tabla = df_tabla[["dt", "aqi", "aqi_descripcion", "pm2_5", "pm10", "no2", "o3", "co", "so2"]]
            df_tabla.columns = ["Hora", "AQI", "Calidad", "PM2.5", "PM10", "NO₂", "O₃", "CO", "SO₂"]

            st.dataframe(
                df_tabla.round(2),
                use_container_width=True,
                column_config={
                    "AQI": st.column_config.NumberColumn(format="%d"),
                    "Calidad": st.column_config.TextColumn(),
                }
            )

        # --- Información adicional ---
        st.markdown("---")
        st.markdown("""
        ### Información sobre la calidad del aire

        **Índice de Calidad del Aire (AQI):**
        - 1 = Buena (verde)
        - 2 = Aceptable (amarillo)
        - 3 = Moderada (naranja)
        - 4 = Mala (rojo)
        - 5 = Muy mala (púrpura)

        **Unidades:** Todas las concentraciones están en μg/m³ (microgramos por metro cúbico)
        """)
