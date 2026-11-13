"""Prueba rápida del entorno y del tema, antes de subir el repo.

Correr desde la carpeta del repo (para que Streamlit lea .streamlit/config.toml):

    streamlit run pruebas/probar_tema.py

No usa el modelo: los números del mapa y de las barras son los que salieron
de las notebooks y están escritos a mano acá. Es solo para probar que todo
anda (paquetes, tema, colores, GeoJSON y datos) en cada compu.
"""

import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))
from componentes import estilo  # noqa: E402

st.set_page_config(page_title="Prueba del tema · DSS Salud Escolar", layout="wide")

st.title("Prueba del entorno y del tema")
st.caption(
    "Si todos los chequeos dan bien y ves los gráficos, el repo está listo para subir. "
    "Los números son de prueba: salen de las notebooks, no del modelo."
)

# ---------------------------------------------------------------------------
# 1. Chequeos
# ---------------------------------------------------------------------------
st.header("1. Chequeos")


def numero_version(texto: str) -> tuple:
    return tuple(int(p) for p in texto.split(".")[:2] if p.isdigit())


# Python
py = sys.version_info
if py >= (3, 10):
    st.success(f"Python {py.major}.{py.minor}.{py.micro}")
else:
    st.error(f"Python {py.major}.{py.minor}: se necesita 3.10 o más nuevo")

# Paquetes de requirements.txt
faltan = []
detalle = []
for paquete in ["pandas", "numpy", "scikit-learn", "scipy", "plotly", "streamlit", "joblib"]:
    try:
        detalle.append(f"{paquete} {version(paquete)}")
    except PackageNotFoundError:
        faltan.append(paquete)
if faltan:
    st.error("Faltan paquetes: " + ", ".join(faltan) + ". Corré `pip install -r requirements.txt`.")
else:
    st.success("Paquetes instalados: " + " · ".join(detalle))

if numero_version(version("streamlit")) < (1, 67):
    st.warning(f"Streamlit {version('streamlit')}: el tema necesita 1.67 o más nuevo. Corré `pip install -U streamlit`.")

# Tema
if st.get_option("theme.primaryColor") == estilo.ACENTO:
    st.success("Tema cálido cargado desde .streamlit/config.toml")
else:
    st.error(
        "No se cargó el tema. Corré `streamlit run pruebas/probar_tema.py` "
        "parado en la carpeta del repo, no adentro de pruebas/."
    )

# GeoJSON
ruta_geo = RAIZ / "data" / "geo" / "provincias.geojson"
geo = None
if ruta_geo.exists():
    geo = json.loads(ruta_geo.read_text(encoding="utf-8"))
    n = len(geo["features"])
    if n == 24:
        st.success("GeoJSON de provincias: 24 provincias")
    else:
        st.error(f"GeoJSON de provincias: tiene {n} provincias en vez de 24")
else:
    st.error("No está data/geo/provincias.geojson")

# Datos de la EMSE
ruta_csv = RAIZ / "data" / "raw" / "data_set.csv"
COLUMNAS_MODELO = ["qn22", "qn23", "qn24", "qn25", "qn26", "qn15", "qn16", "qn66",
                   "qn67", "qn68", "qn29", "qn35", "qn38", "qn42", "qn53"]
if ruta_csv.exists():
    columnas = pd.read_csv(ruta_csv, nrows=0).columns
    faltan_col = [c for c in COLUMNAS_MODELO + ["stratum", "weight"] if c not in columnas]
    if faltan_col:
        st.error("A data_set.csv le faltan columnas: " + ", ".join(faltan_col))
    else:
        filas = len(pd.read_csv(ruta_csv, usecols=["stratum"]))
        st.success(f"data_set.csv: {filas:,} filas y las 17 columnas que usa el modelo".replace(",", "."))
else:
    st.warning("No está data/raw/data_set.csv. Copialo ahí (no se sube al repo).")

# ---------------------------------------------------------------------------
# 2. Cómo se ve el tema
# ---------------------------------------------------------------------------
st.header("2. Cómo se ve el tema")

c1, c2, c3 = st.columns(3)
c1.metric("Estudiantes representados", "2,6 millones")
c2.metric("Respuestas analizadas", "47.945")
c3.metric("Perfiles encontrados", "5")

PAIS = dict(zip(estilo.PERFILES, [37.1, 16.1, 22.4, 13.3, 11.0]))

perfil = st.segmented_control("Perfil", estilo.PERFILES, default="Consumo de riesgo") or "Consumo de riesgo"

# Barras de los 5 perfiles con sus colores fijos
fig_barras = go.Figure(
    go.Bar(
        x=list(PAIS.values()),
        y=estilo.PERFILES,
        orientation="h",
        marker_color=[estilo.COLOR_PERFIL[p] for p in estilo.PERFILES],
        text=[f"{v:.1f}%".replace(".", ",") for v in PAIS.values()],
        textposition="outside",
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    )
)
fig_barras.update_layout(
    title="Estudiantes en cada perfil (% del país)",
    yaxis=dict(autorange="reversed"),
    xaxis=dict(range=[0, 45], ticksuffix="%"),
    height=320,
)
st.plotly_chart(fig_barras, theme=None)

# Mapa con la escala divergente contra el país
PROVINCIAS = {
    "Buenos Aires": [36.1, 14.8, 24.2, 14.4, 10.6], "CABA": [45.3, 12.1, 18.9, 12.0, 11.7],
    "Catamarca": [39.2, 13.7, 21.2, 16.3, 9.6], "Chaco": [36.3, 19.6, 19.2, 11.6, 13.3],
    "Chubut": [40.1, 14.4, 22.1, 14.1, 9.3], "Corrientes": [33.6, 19.6, 20.5, 13.5, 12.7],
    "Córdoba": [35.3, 18.8, 22.9, 10.0, 13.0], "Entre Ríos": [24.6, 21.7, 28.4, 13.4, 11.9],
    "Formosa": [30.1, 16.3, 21.0, 17.0, 15.6], "Jujuy": [45.8, 9.5, 18.1, 18.4, 8.1],
    "La Pampa": [32.8, 19.7, 25.8, 9.9, 11.8], "La Rioja": [44.4, 10.9, 19.9, 14.7, 10.1],
    "Mendoza": [39.1, 16.5, 23.7, 11.1, 9.7], "Misiones": [37.0, 18.9, 17.7, 13.6, 12.8],
    "Neuquén": [37.8, 15.3, 23.6, 13.6, 9.8], "Río Negro": [35.0, 14.8, 29.3, 11.4, 9.4],
    "Salta": [41.7, 12.2, 20.3, 16.7, 9.1], "San Juan": [37.1, 17.4, 20.8, 12.8, 11.9],
    "San Luis": [38.9, 15.6, 23.4, 10.7, 11.4], "Santa Cruz": [40.2, 14.0, 23.4, 12.7, 9.6],
    "Santa Fe": [32.0, 19.0, 24.8, 12.9, 11.4], "Santiago del Estero": [43.0, 14.7, 17.9, 13.1, 11.2],
    "Tierra del Fuego": [38.5, 12.8, 21.9, 16.7, 10.1], "Tucumán": [43.3, 24.8, 13.9, 9.3, 8.7],
}
i = estilo.PERFILES.index(perfil)
df = pd.DataFrame({"provincia": list(PROVINCIAS), "valor": [v[i] for v in PROVINCIAS.values()]})
etiquetas = [nombre for nombre, _ in estilo.CATEGORIAS_VS_PAIS]
df["categoria"] = [etiquetas[estilo.categoria_vs_pais(v, PAIS[perfil])] for v in df["valor"]]

if geo is not None:
    fig_mapa = px.choropleth(
        df,
        geojson=geo,
        locations="provincia",
        featureidkey="properties.provincia",
        color="categoria",
        color_discrete_map=dict(estilo.CATEGORIAS_VS_PAIS),
        category_orders={"categoria": etiquetas},
        hover_name="provincia",
        hover_data={"valor": ":.1f", "provincia": False, "categoria": False},
        labels={"valor": f"% en {perfil}"},
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    fig_mapa.update_traces(marker_line_color="#FFFFFF", marker_line_width=0.8)
    fig_mapa.update_layout(
        title=f"{perfil}: cada provincia contra el país ({PAIS[perfil]:.1f}%)".replace(".", ","),
        height=640,
        legend=dict(orientation="v", y=0.5, x=1.0, title_text=""),
    )
    evento = st.plotly_chart(fig_mapa, theme=None, on_select="rerun", selection_mode="points", key="mapa")

    puntos = evento.selection.points if evento and evento.selection else []
    if puntos:
        st.info(f"Provincia elegida en el mapa: **{puntos[0].get('location')}**")
    else:
        st.caption("Hacé clic en una provincia para probar la selección (la vamos a usar para el detalle).")
