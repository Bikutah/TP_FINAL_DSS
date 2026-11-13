"""Punto de entrada de la app. Desde la carpeta del repo:

    streamlit run app/Inicio.py
"""

import streamlit as st

from componentes import datos, ui

st.set_page_config(page_title="DSS Salud Escolar", page_icon=":material/school:", layout="wide")
ui.aplicar_estilo()
datos.asegurar_artefactos()

paginas = [
    st.Page("paginas/resumen.py", title="Resumen", icon=":material/home:", default=True),
    st.Page("paginas/perfiles.py", title="Perfiles", icon=":material/groups:"),
    st.Page("paginas/provincias.py", title="Provincias", icon=":material/location_on:"),
    st.Page("paginas/modelo.py", title="Cómo se armó el modelo", icon=":material/tune:"),
]
navegacion = st.navigation(paginas)
st.sidebar.caption("Fuente: EMSE 2018 (OMS y Ministerio de Salud). Uso académico.")
navegacion.run()
