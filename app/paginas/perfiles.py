"""Perfiles: ¿qué tiene cada grupo?"""

from html import escape

import streamlit as st

from componentes import datos, estilo, graficos, ui
from componentes.ui import pct

perfiles = datos.perfiles().set_index("perfil")
centroides = datos.centroides()
contexto = datos.contexto()
edad = datos.por_edad()
sexo = datos.por_sexo()

ui.encabezado(
    "¿Qué tiene cada perfil?",
    "Elegí un perfil para ver qué porcentaje de sus estudiantes responde que sí a cada pregunta, "
    "comparado con el total del país.",
)

perfil = st.segmented_control(
    "Perfil", estilo.PERFILES, default="Consumo de riesgo", required=True,
    key="perfil_perfiles", label_visibility="collapsed",
)

# --- Perfil elegido --------------------------------------------------------
fila = perfiles.loc[perfil]
tono, tinte = estilo.TONO_PERFIL[perfil], estilo.TINTE_PERFIL[perfil]
chip = "No requiere acción" if fila["accion"] == "Sin acción" else f"Acción sugerida: {fila['accion']}"
st.html(
    f'<section class="dss-elegido" style="background:{tinte}" aria-label="Perfil elegido">'
    f'<div><div class="pct" style="color:{tono}">{pct(fila["pct"])}</div>'
    f'<div class="estim">{ui.miles(fila["estudiantes_estimados"])} estudiantes</div></div>'
    f'<div class="medio"><span class="nombre">{escape(perfil)}</span>'
    f'<span class="desc">{escape(fila["descripcion"])}</span></div>'
    f'<span class="dss-chip" style="color:{tono}">{escape(chip)}</span></section>'
)

# --- Vector de promedios ---------------------------------------------------
with ui.tarjeta("vector"):
    ui.titulo_tarjeta("¿Qué responde que sí?", "Vector de promedios del grupo: % de sus estudiantes que responde que sí.")
    ui.referencias([("barrita", estilo.COLOR_PERFIL[perfil], perfil), ("rayita", "", "Total del país")])
    for dimension, filas in centroides.groupby("dimension", sort=False):
        st.html(f'<p class="dss-grupo">{escape(dimension)}</p>')
        graficos.mostrar(graficos.barras_vector_promedio(filas, perfil), key=f"vector_{dimension}")

# --- Cruces ----------------------------------------------------------------
col_edad, col_sexo, col_ctx = st.columns(3)

with col_edad, ui.tarjeta("edad"):
    ui.titulo_tarjeta("Por edad", "% de cada edad que está en este perfil")
    graficos.mostrar(graficos.barras_verticales([str(e) for e in edad.index], edad[perfil].tolist(),
                                                estilo.COLOR_PERFIL[perfil], titulo_x="Edad (años)"))

with col_sexo, ui.tarjeta("sexo"):
    ui.titulo_tarjeta("Por sexo", "% de mujeres y de varones que está en este perfil")
    mujeres, varones = sexo.loc["Mujer", perfil], sexo.loc["Varón", perfil]
    graficos.mostrar(graficos.barras_horizontales(["Mujeres", "Varones"], [mujeres, varones],
                                                  estilo.COLOR_PERFIL[perfil]))
    if abs(mujeres - varones) < 1.5:
        st.write("Es parecido en mujeres y en varones.")
    else:
        mas = "mujeres" if mujeres > varones else "varones"
        st.write(f"Es más común en {mas} ({pct(max(mujeres, varones))} contra {pct(min(mujeres, varones))}).")

with col_ctx, ui.tarjeta("contexto"):
    ui.titulo_tarjeta("Contexto", "Preguntas que no entran al modelo y sirven para describir al grupo")
    filas_html = "".join(
        f'<div class="dss-fila"><span class="etiqueta">{escape(c["descripcion"])}</span>'
        f'<span class="valores"><b>{pct(c[perfil])}</b><span>país {pct(c["Total país"])}</span></span></div>'
        for _, c in contexto.iterrows()
    )
    st.html(filas_html)
