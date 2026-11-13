"""Gestión de datos: de data_set.csv a una tabla lista para el k-means."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from src import config


@dataclass
class DatosPreparados:
    base: pd.DataFrame       # todos los estudiantes de 13 a 17 años (con vacíos)
    completos: pd.DataFrame  # solo los que tienen los 15 indicadores respondidos


def a_binaria(serie: pd.Series, valor_si: int = 1) -> pd.Series:
    """1 si la respuesta es valor_si, 0 si respondió otra cosa, NaN si está vacía."""
    return (serie == valor_si).astype(float).where(serie.notna())


def cargar(ruta: Path = config.RUTA_DATOS) -> pd.DataFrame:
    if not ruta.exists():
        raise FileNotFoundError(
            f"No encuentro {ruta}. Bajá data_set.csv de la EMSE 2018 y ponelo en data/raw/."
        )
    return pd.read_csv(ruta)


def preprocesar(crudo: pd.DataFrame) -> DatosPreparados:
    # 1. Estudiantes de 13 a 17 años
    base = crudo[crudo["q1"].isin(config.EDAD_POR_CODIGO)].copy()
    base["edad"] = base["q1"].map(config.EDAD_POR_CODIGO).astype(int)
    base["sexo"] = base["q2"].map(config.SEXO_POR_CODIGO)

    # 2. Provincia desde stratum
    codigo = base["stratum"].astype(str).str[4:6]
    base["provincia"] = codigo.map(config.PROVINCIAS)
    base["provincia_deducida"] = codigo.isin(config.PROVINCIAS_DEDUCIDAS)
    if base["provincia"].isna().any():
        raise ValueError("Hay códigos de provincia en stratum que no están en config.PROVINCIAS")

    # 3. Indicadores del modelo y de contexto a 0/1
    for nombre, (columna, _, _) in config.VARIABLES_MODELO.items():
        base[nombre] = a_binaria(base[columna])
    for nombre, (columna, valor_si, _) in config.VARIABLES_CONTEXTO.items():
        base[nombre] = a_binaria(base[columna], valor_si)
    base["mujer"] = (base["sexo"] == "Mujer").astype(float).where(base["sexo"].notna())

    # 4. Solo filas con los 15 indicadores respondidos
    base["completo"] = base[config.COLUMNAS_MODELO].notna().all(axis=1)
    completos = base[base["completo"]].copy()
    completos[config.COLUMNAS_MODELO] = completos[config.COLUMNAS_MODELO].astype(int)

    columnas = (["record", "weight", "provincia", "provincia_deducida", "edad", "sexo", "mujer"]
                + list(config.VARIABLES_CONTEXTO) + config.COLUMNAS_MODELO)
    return DatosPreparados(base=base, completos=completos[columnas].reset_index(drop=True))


def matriz_modelo(completos: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """X (estudiantes × 15 indicadores, 0/1) y los pesos de la muestra."""
    return completos[config.COLUMNAS_MODELO].to_numpy(dtype=float), completos["weight"].to_numpy()
