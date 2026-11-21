"""Clasificar un estudiante: el modelo k-means entrenado, funcionando en vivo.

Carga artefactos/modelo_kmeans.joblib (el mismo modelo que armó los perfiles) y le
asigna un perfil a las respuestas que se marquen en pantalla. No hace falta
responder las 15 preguntas: las que quedan "Sin dato" no se usan para comparar.
"""

from html import escape

import numpy as np
import pandas as pd
import streamlit as st

from componentes import datos, estilo, graficos, ui

SI, NO, SIN_DATO = "Sí", "No", "Sin dato"

guardado = datos.modelo()
kmeans, columnas, nombres = guardado["modelo"], guardado["columnas"], guardado["nombres"]
centroides = kmeans.cluster_centers_
preguntas = datos.centroides().set_index("indicador").loc[columnas]
perfiles = datos.perfiles().set_index("perfil")


def clave(columna: str) -> str:
    return f"respuesta3_{columna}"


def cargar_ejemplo(perfil: str):
    """Responde las 15 preguntas como la mayoría de ese perfil."""
    for c in columnas:
        st.session_state[clave(c)] = SI if preguntas.loc[c, perfil] >= 50 else NO


def limpiar():
    for c in columnas:
        st.session_state[clave(c)] = SIN_DATO


# La primera vez (o al volver a la página) arranca con un estudiante del que se sabe poco
if any(clave(c) not in st.session_state for c in columnas):
    limpiar()
    st.session_state[clave("alcohol")] = SI
    st.session_state[clave("borrachera")] = SI

ui.encabezado(
    "¿A qué perfil pertenece un estudiante?",
    "Marcá lo que sepas de un estudiante. No hace falta responder todo: "
    "el modelo compara solo las preguntas que tienen respuesta.",
)

st.html(
    '<ol class="dss-pasos" aria-label="Qué hace el modelo">'
    '<li class="dss-paso"><span class="numero" aria-hidden="true">1</span><span class="titulo">Arma el vector</span>'
    '<span class="texto">Cada respuesta pasa a 1 (sí) o 0 (no). Las que quedan sin dato no se cuentan.</span></li>'
    '<li class="dss-paso"><span class="numero" aria-hidden="true">2</span><span class="titulo">Mide distancias</span>'
    '<span class="texto">Compara esas respuestas con el centroide de cada uno de los 5 perfiles.</span></li>'
    '<li class="dss-paso"><span class="numero" aria-hidden="true">3</span><span class="titulo">Elige el más cercano</span>'
    '<span class="texto">El perfil con la distancia más corta es el que le asigna.</span></li>'
    "</ol>"
)

# --- Respuestas ---------------------------------------------------------------
with ui.tarjeta("respuestas"):
    ui.titulo_tarjeta("Respuestas del estudiante", "Sí, No o Sin dato en cada pregunta.")
    botones = st.container(horizontal=True, vertical_alignment="center")
    botones.markdown("**Cargar un estudiante típico:**")
    for p in estilo.PERFILES:
        botones.button(p, on_click=cargar_ejemplo, args=(p,), key=f"ejemplo_{p}", icon=":material/person:")
    botones.button("Todo sin dato", on_click=limpiar, key="limpiar", icon=":material/close:")

    columnas_ui = st.columns(4, gap="medium")
    for col, (dimension, filas) in zip(columnas_ui, preguntas.groupby("dimension", sort=False)):
        with col:
            st.html(f'<p class="dss-grupo">{escape(dimension)}</p>')
            for indicador, fila in filas.iterrows():
                st.segmented_control(fila["descripcion"], [SI, NO, SIN_DATO], key=clave(indicador),
                                     required=True)

# --- El modelo en acción ----------------------------------------------------------
respuestas = [st.session_state[clave(c)] for c in columnas]
vector = np.array([1.0 if r == SI else 0.0 if r == NO else np.nan for r in respuestas])
respondidas = ~np.isnan(vector)
n = int(respondidas.sum())

if n == 0:
    st.info("Marcá al menos una respuesta para que el modelo pueda asignar un perfil.", icon=":material/info:")
    st.stop()

# Distancia al cuadrado a cada centroide, solo en las preguntas respondidas.
# Con las 15 respondidas es la misma cuenta que hace kmeans.predict.
distancia = ((centroides[:, respondidas] - vector[respondidas]) ** 2).sum(axis=1)
grupo = int(np.argmin(distancia))
if n == len(columnas):
    assert grupo == int(kmeans.predict(vector.reshape(1, -1))[0])
perfil = nombres[grupo]
tabla = pd.DataFrame({"perfil": [nombres[i] for i in range(len(distancia))], "distancia": distancia})
tabla = tabla.sort_values("distancia").reset_index(drop=True)

fila = perfiles.loc[perfil]
accion, cuando = fila["accion"], fila.get("cuando", "")
if accion == "Sin acción":
    accion, cuando = "Sin acción específica", "Seguimiento general, como al resto del curso."
ui.accion_sugerida("este estudiante", accion, cuando,
                   f"El modelo lo ubicó en {perfil}: {fila['descripcion'].lower()}.")

col_res, col_dist = st.columns([2, 3], gap="medium")

with col_res:
    tono, tinte = estilo.TONO_PERFIL[perfil], estilo.TINTE_PERFIL[perfil]
    st.html(
        f'<section class="dss-elegido" style="background:{tinte}" aria-label="Perfil asignado">'
        f'<div class="medio"><span class="rotulo">Perfil asignado por el modelo</span>'
        f'<span class="nombre" style="color:{tono}">{escape(perfil)}</span>'
        f'<span class="desc">{escape(fila["descripcion"])}</span></div></section>'
    )

    # Qué tan clara es la asignación: cuánto le gana el primero al segundo
    primero, segundo = tabla.iloc[0], tabla.iloc[1]
    ventaja = (segundo["distancia"] - primero["distancia"]) / segundo["distancia"] if segundo["distancia"] else 0
    if ventaja < 0.15:
        claridad = f"Está en el límite entre {primero['perfil']} y {segundo['perfil']}."
    else:
        claridad = f"Asignación clara: el segundo más cercano es {segundo['perfil']}."
    ui.kpis([(f"{n} de {len(columnas)}", "preguntas respondidas que usó el modelo")])
    ui.nota(claridad + (" Con más respuestas, la asignación es más confiable." if n < len(columnas) else ""))

    por_dimension = []
    for _, filas in preguntas.groupby("dimension", sort=False):
        marcas = []
        for c in filas.index:
            r = st.session_state[clave(c)]
            marcas.append("1" if r == SI else "0" if r == NO else "–")
        por_dimension.append(" ".join(marcas))
    st.html(
        '<div class="dss-vector"><span class="chico">Así lo ve el modelo (1 = sí, 0 = no, – = sin dato)</span>'
        f'<code>{" · ".join(por_dimension)}</code></div>'
    )

with col_dist, ui.tarjeta("distancias"):
    ui.titulo_tarjeta("¿Qué tan cerca quedó de cada perfil?",
                      "Distancia a cada centroide en las preguntas respondidas: la más corta gana.")
    graficos.mostrar(graficos.distancias(tabla, perfil))
