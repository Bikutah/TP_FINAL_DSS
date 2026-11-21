"""Carga de artefactos (los resultados del modelo). La app no calcula nada del modelo."""

import json
import warnings
from pathlib import Path

import joblib

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[2]
ARTEFACTOS = RAIZ / "artefactos"
RUTA_GEO = RAIZ / "data" / "geo" / "provincias.geojson"

NECESARIOS = [
    "perfiles.csv", "centroides.csv", "contexto_por_perfil.csv", "perfiles_por_edad.csv",
    "perfiles_por_sexo.csv", "perfiles_por_provincia.csv", "perfiles_por_provincia_y_edad.csv",
    "acciones_por_provincia.csv", "metricas_modelo.json", "dendrograma.json", "modelo_final.joblib",
]


def asegurar_artefactos():
    faltan = [n for n in NECESARIOS if not (ARTEFACTOS / n).exists()]
    if faltan:
        st.error("Faltan resultados del modelo en artefactos/: " + ", ".join(faltan))
        st.markdown("Corré `python scripts/entrenar.py` desde la carpeta del repo y volvé a abrir la app.")
        st.stop()


@st.cache_data
def _csv(nombre: str) -> pd.DataFrame:
    return pd.read_csv(ARTEFACTOS / f"{nombre}.csv", encoding="utf-8")


@st.cache_data
def _json(nombre: str) -> dict:
    return json.loads((ARTEFACTOS / f"{nombre}.json").read_text(encoding="utf-8"))


@st.cache_data
def geojson() -> dict:
    return json.loads(RUTA_GEO.read_text(encoding="utf-8"))


def perfiles() -> pd.DataFrame:
    return _csv("perfiles")


def pais() -> pd.Series:
    """% de estudiantes del país en cada perfil."""
    return perfiles().set_index("perfil")["pct"]


def centroides() -> pd.DataFrame:
    return _csv("centroides")


def contexto() -> pd.DataFrame:
    return _csv("contexto_por_perfil")


def por_edad() -> pd.DataFrame:
    return _csv("perfiles_por_edad").set_index("edad")


def por_sexo() -> pd.DataFrame:
    return _csv("perfiles_por_sexo").set_index("sexo")


def por_provincia() -> pd.DataFrame:
    return _csv("perfiles_por_provincia").set_index("provincia")


def por_provincia_y_edad() -> pd.DataFrame:
    return _csv("perfiles_por_provincia_y_edad")


def acciones() -> pd.DataFrame:
    return _csv("acciones_por_provincia").set_index("provincia")


def metricas() -> dict:
    return _json("metricas_modelo")


def dendrograma() -> dict:
    return _json("dendrograma")


@st.cache_resource
def modelo() -> dict:
    """El modelo final elegido en el notebook evaluacion-modelos-v2 (k-means, k = 5).

    {"modelo": KMeans, "variables": las 15 columnas en orden, "nombres": {grupo: perfil},
     "riesgo_suicida": indicadores que disparan la advertencia}
    """
    with warnings.catch_warnings():
        # Se guardó con scikit-learn 1.9.1. Con otra versión avisa, pero el modelo carga igual.
        warnings.simplefilter("ignore")
        return joblib.load(ARTEFACTOS / "modelo_final.joblib")
