"""Resumen: ¿qué perfiles hay y cuántos estudiantes son?"""

import streamlit as st

from componentes import datos, estilo, graficos, ui
from componentes.ui import num, pct

perfiles = datos.perfiles()
metricas = datos.metricas()
edad = datos.por_edad()

ui.encabezado(
    "¿Qué perfiles hay y cuántos estudiantes son?",
    "Así se agrupan los estudiantes de 13 a 17 años según las problemáticas que tienen juntas "
    "(EMSE 2018, k-means).",
)

ui.kpis([
    (ui.millones(metricas["poblacion_representada"]), "estudiantes representados"),
    (num(metricas["estudiantes_modelo"], 0), "respuestas analizadas"),
    (f"{metricas['k']} perfiles", "encontrados en los datos"),
])

izq, der = st.columns([3, 1], vertical_alignment="bottom")
izq.subheader(f"Los {metricas['k']} perfiles")
der.page_link("paginas/perfiles.py", label="Ver qué tiene cada perfil", icon=":material/arrow_forward:")
ui.tarjetas_perfiles(perfiles)

riesgo = edad["Consumo de riesgo"]
ui.callout(
    f"El consumo de riesgo pasa del {pct(riesgo.iloc[0], 0)} a los {edad.index[0]} años "
    f"al {pct(riesgo.iloc[-1], 0)} a los {edad.index[-1]}.",
    "La prevención tiene que llegar antes de los 15.",
)

with ui.tarjeta("edad"):
    ui.titulo_tarjeta("¿En qué perfil está cada edad?", "Cada barra suma 100%: todos los estudiantes de esa edad.")
    ui.referencias([("punto", estilo.COLOR_PERFIL[p], p) for p in perfiles["perfil"]])
    graficos.mostrar(graficos.barras_apiladas(edad, [f"{e} años" for e in edad.index]))
