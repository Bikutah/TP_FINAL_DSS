"""Cómo se armó el modelo: ¿cómo se hicieron los grupos y cuánto podemos confiar?"""

from html import escape

import streamlit as st

from componentes import datos, graficos, ui
from componentes.ui import num, pct

metricas = datos.metricas()
dendro = datos.dendrograma()
k = metricas["k"]

ui.encabezado(
    "¿Cómo se armaron los grupos y cuánto podemos confiar?",
    "El camino de las respuestas a los perfiles, para quien quiera revisar el método.",
)

pasos = [
    ("Datos", f"{num(metricas['estudiantes_modelo'], 0)} estudiantes de 13 a 17 años con las 15 respuestas "
              f"completas ({pct(metricas['pct_completos'], 0)} del total)."),
    ("15 indicadores sí/no", "Salud mental, violencia, consumo y faltas. Cada uno vale 1 si responde que sí."),
    ("Cuántos grupos", f"Método del codo y dendrograma: desde k = {k}, sumar grupos aporta poco."),
    ("K-means con pesos", f"{metricas['parametros']['semillas']} semillas × {metricas['parametros']['n_init']} "
                          "arranques, con los pesos de la muestra. Queda la de menor inercia."),
    ("Nombrar y cruzar", "Cada centroide se lee como % que dice que sí. Después se cruza con provincia, edad y sexo."),
]
st.html(
    '<ol class="dss-pasos" aria-label="Pasos del modelo">'
    + "".join(
        f'<li class="dss-paso"><span class="numero" aria-hidden="true">{i}</span>'
        f'<span class="titulo">{escape(t)}</span><span class="texto">{escape(d)}</span></li>'
        for i, (t, d) in enumerate(pasos, start=1)
    )
    + "</ol>"
)

col_codo, col_dendro = st.columns(2, gap="medium")
with col_codo, ui.tarjeta("codo"):
    ui.titulo_tarjeta(f"Desde k = {k}, sumar grupos mejora poco",
                      "Método del codo: inercia (millones) según la cantidad de grupos.")
    graficos.mostrar(graficos.codo(metricas["codo"], k))

with col_dendro, ui.tarjeta("dendrograma"):
    ui.titulo_tarjeta(f"Cortando en la línea quedan {k} grupos",
                      f"Dendrograma (Ward) sobre una muestra de {num(dendro['muestra'], 0)} estudiantes.")
    graficos.mostrar(graficos.dendrograma(dendro["icoord"], dendro["dcoord"], dendro["corte"], k))

estables = sum(s["ari"] >= 0.99 for s in metricas["semillas"])
silueta = metricas["silueta"][str(k)]
st.html(
    '<section class="dss-confianza" aria-label="Cuánto podemos confiar">'
    f'<div class="verde"><span class="valor">{estables} de {len(metricas["semillas"])}</span>'
    '<span class="texto">semillas dan los mismos grupos (ARI ≥ 0,99; 1 = idénticos).</span></div>'
    f'<div><span class="valor">{num(silueta, 2)}</span>'
    f'<span class="texto">de silueta (de -1 a 1): los perfiles se superponen en parte, algo esperable con '
    'respuestas sí/no.</span></div>'
    '<div><span class="valor">Sin estandarizar</span>'
    '<span class="texto">Todas las variables son 0/1: la distancia cuenta en cuántas respuestas difieren '
    'dos estudiantes.</span></div></section>'
)

ui.nota(
    f"Límites: datos de 2018 y autorreportados; el {pct(100 - metricas['pct_completos'], 0)} de las respuestas "
    f"quedó afuera por faltantes (entre {pct(metricas['excluidos_por_provincia_min'], 0)} y "
    f"{pct(metricas['excluidos_por_provincia_max'], 0)} según la provincia); 6 nombres de provincia son deducidos."
)
