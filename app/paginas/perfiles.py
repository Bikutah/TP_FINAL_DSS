"""Perfiles: ¿qué tiene cada grupo?"""

from html import escape

import pandas as pd
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
    "Elegí un perfil para ver en qué se diferencia del resto del país.",
)

perfil = st.segmented_control(
    "Perfil", estilo.PERFILES, default="Consumo de riesgo", required=True,
    key="perfil_perfiles", label_visibility="collapsed",
)
color = estilo.COLOR_PERFIL[perfil]

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

# --- Perfil contra el país ---------------------------------------------------
# Los 15 indicadores del modelo y, al final, las preguntas de contexto, todos con el mismo gráfico
ctx = contexto.rename(columns={"variable": "indicador"}).assign(
    dimension="Otras características (no se usaron para armar los grupos)")
comparacion = pd.concat([centroides, ctx], ignore_index=True)

with ui.tarjeta("vector"):
    ui.titulo_tarjeta(f"{perfil} contra todo el país", "% que respondió que sí a cada pregunta")
    ui.referencias([("barrita", estilo.COLOR_COMPARACION[perfil], perfil),
                    ("barrita", estilo.COLOR_PAIS, "Todo el país")])
    grupos = list(comparacion.groupby("dimension", sort=False))
    for i, (dimension, filas) in enumerate(grupos):
        st.html(f'<p class="dss-grupo">{escape(dimension)}</p>')
        graficos.mostrar(
            graficos.barras_contra_pais(filas["descripcion"].tolist(), filas[perfil].tolist(),
                                        filas["Total país"].tolist(), perfil,
                                        mostrar_escala=i == len(grupos) - 1),
            key=f"vector_{i}",
        )


# --- Por edad y por sexo -----------------------------------------------------
def tendencia(valores) -> str:
    """Título que resume cómo cambia el perfil con la edad."""
    primero, ultimo = valores.iloc[0], valores.iloc[-1]
    pico = valores.idxmax()
    if valores.max() - max(primero, ultimo) >= 3:
        return f"Llega al máximo a los {pico} años"
    if ultimo - primero >= 3:
        return "Crece con la edad"
    if primero - ultimo >= 3:
        return "Baja con la edad"
    return "Parecido en todas las edades"


col_edad, col_sexo = st.columns(2, gap="medium")

with col_edad, ui.tarjeta("edad"):
    ui.titulo_tarjeta(tendencia(edad[perfil]), "% de cada edad que está en este perfil")
    graficos.mostrar(graficos.barras_verticales([str(e) for e in edad.index], edad[perfil].tolist(),
                                                color, titulo_x="Edad (años)"))

with col_sexo, ui.tarjeta("sexo"):
    mujeres, varones = sexo.loc["Mujer", perfil], sexo.loc["Varón", perfil]
    if abs(mujeres - varones) < 1.5:
        titulo = "Parecido en mujeres y varones"
    else:
        titulo = f"Más común en {'mujeres' if mujeres > varones else 'varones'}"
    ui.titulo_tarjeta(titulo, "% de todas las mujeres y de todos los varones que está en este perfil")
    graficos.mostrar(graficos.barras_horizontales(["Mujeres", "Varones"], [mujeres, varones], color, alto=180))
