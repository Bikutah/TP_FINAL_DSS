"""Clasificar un estudiante: el modelo final, funcionando en vivo.

Carga artefactos/modelo_final.joblib, el k-means elegido en el notebook
evaluacion-modelos-v2, y le asigna un perfil a las respuestas que se marquen.

Como pidió la cátedra (observación 4 del notebook v2):
- Hay que responder las 15 preguntas, que es el criterio con el que se entrenó el
  modelo. Si falta alguna, no se asigna perfil y se dice cuáles faltan.
- Si el estudiante marca ideación, plan o intento de suicidio, se muestra una
  advertencia, cualquiera sea el perfil y aunque falten respuestas.

Diseño: preguntas a la izquierda (un grupo por fila) y, a la derecha, un panel que
acompaña el scroll con la acción sugerida en grande (ver .st-key-panel_resultado en estilo.css).
"""

from html import escape

import numpy as np
import pandas as pd
import streamlit as st

from componentes import datos, estilo, graficos, ui

SI, NO = "Sí", "No"

guardado = datos.modelo()
kmeans, columnas, nombres = guardado["modelo"], guardado["variables"], guardado["nombres"]
riesgo_suicida = guardado["riesgo_suicida"]
centroides = kmeans.cluster_centers_
preguntas = datos.centroides().set_index("indicador").loc[columnas]
perfiles = datos.perfiles().set_index("perfil")


def clave(columna: str) -> str:
    return f"respuesta4_{columna}"


def cargar_ejemplo(perfil: str):
    """Responde las 15 preguntas como la mayoría de ese perfil."""
    for c in columnas:
        st.session_state[clave(c)] = SI if preguntas.loc[c, perfil] >= 50 else NO


def borrar():
    for c in columnas:
        st.session_state[clave(c)] = None


# La primera vez (o al volver a la página) arranca sin ninguna respuesta
if any(clave(c) not in st.session_state for c in columnas):
    borrar()

ui.encabezado(
    "¿A qué perfil pertenece un estudiante?",
    "Respondé Sí o No en las 15 preguntas. El modelo se entrenó con las 15, "
    "así que solo asigna un perfil cuando están todas respondidas.",
)

with st.expander("¿Cómo decide el modelo?"):
    st.html(
        '<ol class="dss-pasos" aria-label="Qué hace el modelo">'
        '<li class="dss-paso"><span class="numero" aria-hidden="true">1</span><span class="titulo">Arma el vector</span>'
        '<span class="texto">Cada una de las 15 respuestas pasa a 1 (sí) o 0 (no).</span></li>'
        '<li class="dss-paso"><span class="numero" aria-hidden="true">2</span><span class="titulo">Mide distancias</span>'
        '<span class="texto">Compara el vector con el centroide de cada uno de los 5 perfiles.</span></li>'
        '<li class="dss-paso"><span class="numero" aria-hidden="true">3</span><span class="titulo">Elige el más cercano</span>'
        '<span class="texto">El perfil con la distancia más corta es el que le asigna.</span></li>'
        "</ol>"
    )

col_preguntas, col_panel = st.columns([1.6, 1], gap="medium")

# --- Respuestas (izquierda): un grupo por fila -----------------------------------
with col_preguntas, ui.tarjeta("respuestas"):
    ui.titulo_tarjeta("Respuestas del estudiante", "Sí o No en cada una de las 15 preguntas.")
    botones = st.container(horizontal=True, vertical_alignment="center")
    botones.markdown("**Cargar un estudiante típico:**")
    for p in estilo.PERFILES:
        botones.button(p, on_click=cargar_ejemplo, args=(p,), key=f"ejemplo_{p}", icon=":material/person:")
    botones.button("Borrar respuestas", on_click=borrar, key="borrar", icon=":material/close:")

    # El título del grupo a la izquierda y sus preguntas una al lado de la otra.
    # Todas las filas tienen 5 lugares, así las preguntas quedan alineadas entre grupos, y
    # van alineadas abajo: aunque un título ocupe dos líneas, los Sí / No quedan a la misma altura.
    grupos = list(preguntas.groupby("dimension", sort=False))
    lugares = max(len(filas) for _, filas in grupos)
    for i, (dimension, filas) in enumerate(grupos):
        if i:
            st.divider()
        titulo, *celdas = st.columns([1] + [1] * lugares, gap="small", vertical_alignment="bottom")
        titulo.html(f'<p class="dss-grupo">{escape(dimension)}</p>')
        for celda, (indicador, fila) in zip(celdas, filas.iterrows()):
            with celda:
                st.segmented_control(fila["descripcion"], [SI, NO], key=clave(indicador))

respuestas = {c: st.session_state[clave(c)] for c in columnas}
faltan = [c for c in columnas if respuestas[c] is None]
marcados = [c for c in riesgo_suicida if respuestas[c] == SI]

# --- Panel de resultado (derecha, acompaña el scroll) ---------------------------
with col_panel, st.container(key="panel_resultado"):
    # Advertencia de riesgo suicida: no depende del perfil y sale aunque falten respuestas
    if marcados:
        lista = ", ".join(preguntas.loc[c, "descripcion"].lower() for c in marcados)
        st.html(
            '<div class="dss-advertencia" role="note">'
            f"<strong>Advertencia:</strong> el estudiante respondió que sí a: {escape(lista)}. "
            "Esto pide atención individual de un profesional, más allá del perfil que le asigne el modelo."
            "</div>"
        )

    if faltan:
        # Sin las 15 respuestas no hay asignación: se reserva el lugar de la acción y se muestra el progreso
        n = len(columnas) - len(faltan)
        lista = ", ".join(preguntas.loc[c, "descripcion"].lower() for c in faltan)
        st.html(
            '<section class="dss-accion-vacia" aria-label="Acción sugerida">'
            '<span class="rotulo">Acción sugerida para este estudiante</span>'
            '<span class="titulo">Aparece al completar las 15 respuestas</span></section>'
        )
        with ui.tarjeta("progreso"):
            st.html(
                '<div class="dss-progreso">'
                f'<span class="valor">{n} de {len(columnas)}</span><span class="chico">respuestas</span>'
                f'<div class="barra"><i style="width:{n / len(columnas):.0%}"></i></div>'
                f'<span class="chico">No es posible una asignación válida todavía. Faltan: {escape(lista)}.</span>'
                "</div>"
            )
        st.stop()

    # --- El modelo en acción ------------------------------------------------------
    vector = np.array([1.0 if respuestas[c] == SI else 0.0 for c in columnas])
    distancia = ((centroides - vector) ** 2).sum(axis=1)  # la misma cuenta que kmeans.predict
    grupo = int(kmeans.predict(vector.reshape(1, -1))[0])
    assert grupo == int(np.argmin(distancia))
    perfil = nombres[grupo]
    tabla = pd.DataFrame({"perfil": [nombres[i] for i in range(len(distancia))], "distancia": distancia})
    tabla = tabla.sort_values("distancia").reset_index(drop=True)

    fila = perfiles.loc[perfil]
    accion, cuando = fila["accion"], fila.get("cuando", "")
    if accion == "Sin acción":
        accion, cuando = "Sin acción específica", "Seguimiento general, como al resto del curso."
    # Cada cosa en su bloque, como en el diseño original: acción, perfil, distancias y vector

    # 1. Acción sugerida (franja verde con el porqué)
    ui.accion_sugerida("este estudiante", accion, cuando,
                       f"El modelo lo ubicó en {perfil}: {fila['descripcion'].lower()}.")

    # 2. Perfil asignado (tarjeta con el color del perfil)
    tono, tinte = estilo.TONO_PERFIL[perfil], estilo.TINTE_PERFIL[perfil]
    st.html(
        f'<section class="dss-elegido" style="background:{tinte}" aria-label="Perfil asignado">'
        f'<div class="medio"><span class="rotulo">Perfil asignado por el modelo</span>'
        f'<span class="nombre" style="color:{tono}">{escape(perfil)}</span>'
        f'<span class="desc">{escape(fila["descripcion"])}</span></div></section>'
    )

    # 3. Distancias a cada centroide
    with ui.tarjeta("distancias"):
        ui.titulo_tarjeta("¿Qué tan cerca quedó de cada perfil?",
                          "Distancia a cada centroide en las 15 preguntas: la más corta gana.")
        graficos.mostrar(graficos.distancias(tabla, perfil))

    # 4. Qué tan clara es la asignación y cómo ve el modelo al estudiante
    primero, segundo = tabla.iloc[0], tabla.iloc[1]
    ventaja = (segundo["distancia"] - primero["distancia"]) / segundo["distancia"] if segundo["distancia"] else 0
    ui.nota(f"Está en el límite entre {primero['perfil']} y {segundo['perfil']}." if ventaja < 0.15
            else f"Asignación clara: el segundo más cercano es {segundo['perfil']}.")
    por_dimension = [" ".join("1" if respuestas[c] == SI else "0" for c in filas.index)
                     for _, filas in preguntas.groupby("dimension", sort=False)]
    st.html(
        '<div class="dss-vector"><span class="chico">Así lo ve el modelo (1 = sí, 0 = no)</span>'
        f'<code>{" · ".join(por_dimension)}</code></div>'
    )
