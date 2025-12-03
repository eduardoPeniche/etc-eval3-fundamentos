# ETL-Air Pollution API - OpenWeather

## 1. Descripción
Proyecto para la asignatura "Fundamentos de Ingeniería de Datos" que incluye:

- Extracción de datos históricos de contaminación del aire desde la API **Air Pollution** de OpenWeatherMap.
- Transformación de las respuestas JSON a tablas relacionales.
- Carga de los datos en una base de datos SQL (SQLite por defecto).
- Visualización interactiva de la calidad del aire en un dashboard hecho con **Streamlit**.

## 2. Tema: Importancia de la Calidad del Aire en las Ciudades

La calidad del aire es uno de los indicadores ambientales más importantes para la salud y el desarrollo en las ciudades. La contaminación representa un riesgo para la salud, contribuyendo a enfermedades respiratorias.

### ¿Cómo ayuda este proyecto ETL y Dashboard?

Este sistema proporciona:

- Extracción automatizada de datos históricos desde fuentes confiables (OpenWeatherMap API).
- Dashboard interactivo que permite:
  - Visualizar tendencias de calidad del aire por ciudad y fecha.
  - Comparar concentraciones de diferentes contaminantes.
  - Identificar patrones horarios y diarios de contaminación.
  - Facilitar la toma de decisiones para autoridades ambientales.

## 3. Fuente de Datos
**OpenWeatherMap Air Pollution API** - Historial de Contaminación del Aire

Esta API proporciona datos históricos sobre la calidad del aire y concentraciones de contaminantes atmosféricos para ubicaciones específicas alrededor del mundo.

### Datos que proporciona:
- **Índice de Calidad del Aire (AQI)**: Escala de 1-5 (1=Buena, 2=Aceptable, 3=Moderada, 4=Mala, 5=Muy mala)
- **Concentraciones de contaminantes** (en μg/m³):
  - CO (Monóxido de carbono)
  - NO (Monóxido de nitrógeno)
  - NO₂ (Dióxido de nitrógeno)
  - O₃ (Ozono)
  - SO₂ (Dióxido de azufre)
  - PM2.5 (Partículas finas ≤ 2.5 micrómetros)
  - PM10 (Partículas gruesas ≤ 10 micrómetros)
  - NH₃ (Amoníaco)
- **Información temporal**: Datos por hora para rangos históricos específicos
- **Ubicación geográfica**: Coordenadas de latitud y longitud

### Endpoint utilizado:
```
http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start}&end={end}&appid={API_key}
```

**Parámetros requeridos:**
- `lat`, `lon`: Coordenadas geográficas
- `start`, `end`: Rangos de fecha en formato Unix timestamp
- `appid`: Clave de API de OpenWeatherMap


## 4. Requisitos

- Python 3.10+
- Conda (Anaconda o Miniconda)
- Cuenta en [OpenWeatherMap](https://openweathermap.org/) y API key activa para **Air Pollution API**.


## 5. Estructura de carpetas

Estructura del proyecto:

```text
ETL-Air-Pollution/
├─ app/
│  └─ main.py
├─ config/
│  ├─ cities.csv
│  └─ settings.yaml
├─ data/
│  ├─ raw/
│  └─ processed/
├─ sql/
│  └─ schema.sql
├─ src/
│  ├─ etl/
│  │  ├─ extract.py
│  │  ├─ load.py
│  │  ├─ pipeline.py
│  │  └─ transform.py
│  └─ utils/
│     └─ db.py
├─ .env
└─ requirements.txt
```



## 6. Configuración del entorno con conda

Desde la carpeta raíz del proyecto (`ETL-Air-Pollution/`):

```bash
# 1) Crear entorno conda
conda create -n etl-air-pollution python=3.11 -y

# 2) Activar entorno
conda activate etl-air-pollution

# 3) Instalar dependencias (vía pip dentro del entorno conda)
pip install -r requirements.txt
```




## 7. Configuración de variables y archivos de configuración

### 7.1 Archivo `.env`

En la raíz del proyecto, crea un archivo `.env` con el siguiente contenido:

```env
# Clave de la API de contaminación del aire (OpenWeatherMap)
OPENWEATHER_API_KEY=TU_API_KEY_AQUI

# Base de datos: usaremos SQLite en data/pollution.db
DB_URL=sqlite:///./data/pollution.db
```


### 7.2 Archivo `config/cities.csv`

Define las ciudades a monitorear (ejemplo):

```csv
city_name,country,lat,lon
Merida,mx,20.97,-89.62
Mexico City,mx,19.43,-99.13
Monterrey,mx,25.67,-100.31
Guadalajara,mx,20.67,-103.35
```

- `city_name`: nombre de la ciudad.
- `country`: código de país (ISO 2 letras).
- `lat`, `lon`: coordenadas aproximadas.



### 7.3 Archivo `config/settings.yaml`

Ejemplo mínimo de configuración:

```yaml
api:
  base_url: "http://api.openweathermap.org/data/2.5/air_pollution/history"
  # Rango de fechas para datos históricos (formato YYYY-MM-DD)
  start_date: "2024-12-01"
  end_date: "2024-12-03"

etl:
  save_raw: true              # guardar JSON crudos
  raw_path: "data/raw"
  processed_path: "data/processed"
```



### 7.4 Carpetas de datos

Si no existen, créalas:

```bash
mkdir -p data/raw
mkdir -p data/processed
```

En Windows, puedes crear las carpetas manualmente o con:

```bash
mkdir data
aw data\processed
```



## 8. Inicializar base de datos y ejecutar el ETL

El script del pipeline:

- Crea las tablas a partir de `sql/schema.sql` (vía `init_db`).
- Llama a la API para cada ciudad.
- Genera los DataFrames de `dim_city` y `fact_air_pollution`.
- Inserta/actualiza los datos en la base de datos.

Desde la raíz del proyecto, con el entorno conda activado:

```bash
conda activate etl-air-pollution

# Ejecutar el pipeline ETL
python -m src.etl.pipeline
```

Si todo funciona correctamente, deberías ver un mensaje similar a:

```text
[OK] ETL completado correctamente.
```

Y se creará el archivo `data/pollution.db` (base de datos SQLite con datos de contaminación del aire).



## 9. Ejecutar la aplicación Streamlit

Con el entorno `etl-air-pollution` activado:

```bash
conda activate etl-air-pollution
streamlit run app/main.py
```

Esto abrirá automáticamente el navegador o mostrará una URL como:

```text
http://localhost:8501
```

En el dashboard verás:

- **Filtros interactivos**: Selector de ciudad y fecha.
- **Métricas principales**:
  - Índice de Calidad del Aire (AQI) con descripción.
  - Concentraciones de PM2.5, PM10 y NO₂.
- **Visualizaciones**:
  - Gráfico de línea mostrando la evolución del AQI durante el día.
  - Gráfico de barras para comparar concentraciones de contaminantes por hora.
  - Tabla detallada con todas las mediciones.
- **Información educativa** sobre los niveles de calidad del aire.



## 10. Actualizar los datos

Cada vez que quieras refrescar la información de contaminación del aire:

1. Modifica las fechas en `config/settings.yaml` si deseas consultar un período diferente.

2. Ejecuta de nuevo el ETL:

   ```bash
   conda activate etl-air-pollution
   python -m src.etl.pipeline
   ```

3. Regresa al dashboard de Streamlit y recarga la página (o usa el botón **"Rerun"**).