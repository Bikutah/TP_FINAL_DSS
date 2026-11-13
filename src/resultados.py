"""Cruces de los perfiles con provincia, edad y sexo, y guardado de artefactos.

Todos los porcentajes usan los pesos de la muestra (columna weight), así
representan a los estudiantes del país y no solo a los que respondieron.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src import config, reglas
from src.modelo import ResultadoModelo
from src.preprocesamiento import DatosPreparados


def pct_ponderado(datos: pd.DataFrame, columna: str) -> float:
    validos = datos[columna].notna()
    if not validos.any():
        return float("nan")
    return float(100 * np.average(datos.loc[validos, columna], weights=datos.loc[validos, "weight"]))


def mezcla_de_perfiles(datos: pd.DataFrame, por: str | list | None = None) -> pd.DataFrame:
    """% de cada perfil (columnas) dentro de cada grupo de `por` (filas)."""
    if por is None:
        tabla = datos.groupby("perfil")["weight"].sum().to_frame().T
    else:
        tabla = datos.pivot_table(index=por, columns="perfil", values="weight", aggfunc="sum", fill_value=0)
    tabla = tabla.reindex(columns=reglas.PERFILES, fill_value=0)
    return (tabla.div(tabla.sum(axis=1), axis=0) * 100).round(1)


def calcular(prep: DatosPreparados, modelo: ResultadoModelo) -> dict[str, pd.DataFrame | dict]:
    datos = prep.completos.copy()
    km = modelo.kmeans

    # Nombre de cada grupo según su centroide
    centros = pd.DataFrame(km.cluster_centers_, columns=config.COLUMNAS_MODELO)
    nombres = {i: reglas.nombrar(c) for i, c in centros.iterrows()}
    if len(set(nombres.values())) != config.K:
        raise ValueError(f"Dos grupos quedaron con el mismo nombre: {nombres}. Revisar src/reglas.py")
    datos["perfil"] = pd.Series(km.labels_).map(nombres).to_numpy()

    poblacion = float(prep.base["weight"].sum())
    pais = mezcla_de_perfiles(datos).iloc[0]

    # perfiles.csv
    perfiles = pd.DataFrame({
        "perfil": reglas.PERFILES,
        "pct": [pais[p] for p in reglas.PERFILES],
        "estudiantes_estimados": [round(pais[p] / 100 * poblacion) for p in reglas.PERFILES],
        "muestra": [int((datos["perfil"] == p).sum()) for p in reglas.PERFILES],
        "descripcion": [reglas.DESCRIPCION[p] for p in reglas.PERFILES],
        "accion": [reglas.ACCIONES[p][0] for p in reglas.PERFILES],
    })

    # centroides.csv (% que responde que sí en cada perfil y en el país)
    centroides = (centros.rename(index=nombres).T.reindex(columns=reglas.PERFILES) * 100).clip(lower=0).round(1)
    centroides["Total país"] = [round(pct_ponderado(datos, c), 1) for c in config.COLUMNAS_MODELO]
    centroides.insert(0, "dimension", [config.VARIABLES_MODELO[c][2] for c in centroides.index])
    centroides.insert(0, "descripcion", [config.VARIABLES_MODELO[c][1] for c in centroides.index])
    centroides.index.name = "indicador"
    centroides = centroides.reset_index()

    # contexto_por_perfil.csv
    variables = {"mujer": "Es mujer"} | {k: v[2] for k, v in config.VARIABLES_CONTEXTO.items()}
    filas = []
    for var, desc in variables.items():
        fila = {"variable": var, "descripcion": desc}
        for p in reglas.PERFILES:
            fila[p] = round(pct_ponderado(datos[datos["perfil"] == p], var), 1)
        fila["Total país"] = round(pct_ponderado(datos, var), 1)
        filas.append(fila)
    contexto = pd.DataFrame(filas)

    # por edad y por sexo
    por_edad = mezcla_de_perfiles(datos, "edad").reset_index()
    por_sexo = mezcla_de_perfiles(datos.dropna(subset=["sexo"]), "sexo").reset_index()

    # por provincia (estudiantes y respuestas salen de todos los de 13 a 17, con vacíos)
    por_prov = mezcla_de_perfiles(datos, "provincia")
    info = prep.base.groupby("provincia").agg(
        deducida=("provincia_deducida", "first"),
        estudiantes=("weight", "sum"),
        respuestas=("record", "size"),
        excluidos_pct=("completo", lambda s: round(100 * (1 - s.mean()), 1)),
    )
    info["estudiantes"] = info["estudiantes"].round().astype(int)
    por_provincia = info.join(por_prov).reset_index()

    por_provincia_edad = mezcla_de_perfiles(datos, ["provincia", "edad"]).reset_index()

    # acciones_por_provincia.csv
    acciones = pd.DataFrame([
        {"provincia": prov, **reglas.accion_sugerida(por_prov.loc[prov], pais)}
        for prov in por_prov.index
    ])

    # métricas para la pantalla del modelo
    metricas = {
        "k": config.K,
        "estudiantes_modelo": int(len(datos)),
        "estudiantes_13_17": int(len(prep.base)),
        "poblacion_representada": round(poblacion),
        "pct_completos": round(100 * len(datos) / len(prep.base), 1),
        "excluidos_por_provincia_min": float(info["excluidos_pct"].min()),
        "excluidos_por_provincia_max": float(info["excluidos_pct"].max()),
        "codo": {str(k): v for k, v in modelo.codo.items()},
        "silueta": {str(k): v for k, v in modelo.silueta.items()},
        "semillas": modelo.semillas,
        "mejor_semilla": modelo.mejor_semilla,
        "inercia": float(km.inertia_),
        "parametros": {"n_init": config.N_INIT, "semillas": len(config.SEMILLAS),
                       "muestra_silueta": config.MUESTRA_SILUETA},
    }

    return {
        "perfiles": perfiles,
        "centroides": centroides,
        "contexto_por_perfil": contexto,
        "perfiles_por_edad": por_edad,
        "perfiles_por_sexo": por_sexo,
        "perfiles_por_provincia": por_provincia,
        "perfiles_por_provincia_y_edad": por_provincia_edad,
        "acciones_por_provincia": acciones,
        "metricas_modelo": metricas,
        "dendrograma": modelo.dendrograma,
        "_nombres": nombres,
    }


def guardar(resultados: dict, modelo: ResultadoModelo, carpeta: Path = config.CARPETA_ARTEFACTOS) -> list[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    escritos = []
    for nombre, valor in resultados.items():
        if nombre.startswith("_"):
            continue
        if isinstance(valor, pd.DataFrame):
            ruta = carpeta / f"{nombre}.csv"
            valor.to_csv(ruta, index=False, encoding="utf-8")
        else:
            ruta = carpeta / f"{nombre}.json"
            ruta.write_text(json.dumps(valor, ensure_ascii=False, indent=1), encoding="utf-8")
        escritos.append(ruta)
    ruta = carpeta / "modelo_kmeans.joblib"
    joblib.dump({"modelo": modelo.kmeans, "columnas": config.COLUMNAS_MODELO,
                 "nombres": resultados["_nombres"]}, ruta)
    escritos.append(ruta)
    return escritos
