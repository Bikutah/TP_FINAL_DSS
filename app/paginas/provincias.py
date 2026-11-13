"""Provincias: ¿dónde conviene actuar y con qué?"""

from html import escape

import pandas as pd
import streamlit as st

from componentes import datos, estilo, graficos, ui
from componentes.ui import pct

provincias = datos.por_provincia()
acciones = datos.acciones()
por_prov_edad = datos.por_provincia_y_edad()
edad_pais = datos.por_edad()
pais = datos.pais()
etiquetas_cat = [c for c, _ in estilo.CATEGORIAS_VS_PAIS]
COMPARACION = ["Mucho más alto que el país", "Más alto que el país", "Parecido al país",
               "Más bajo que el país", "Mucho más bajo que el país"]

if "provincia" not in st.session_state:
    st.session_state["provincia"] = "Chubut"


def tomar_clic(clave: str, campo: str):
    """Si se hizo clic en el mapa o en el ranking, esa provincia pasa a ser la elegida."""
    estado = st.session_state.get(clave)
    try:
        puntos = estado["selection"]["points"]
    except (TypeError, KeyError):
        puntos = []
    elegido = str(puntos[0].get(campo, "")).rstrip("*") if puntos else ""
    if elegido in provincias.index and elegido != st.session_state.get(f"_ultimo_{clave}"):
        st.session_state[f"_ultimo_{clave}"] = elegido
        st.session_state["provincia"] = elegido


tomar_clic("mapa", "location")
tomar_clic("ranking", "y")
seleccion = st.session_state["provincia"]

ui.encabezado(
    "¿Dónde conviene actuar y con qué?",
    "Elegí un perfil y tocá una provincia para ver su detalle.",
)

perfil = st.segmented_control(
    "Perfil", estilo.PERFILES, default="Consumo de riesgo", required=True,
    key="perfil_provincias", label_visibility="collapsed",
)
valor_pais = float(pais[perfil])

tabla = pd.DataFrame({
    "provincia": provincias.index,
    "etiqueta": [p + ("*" if d else "") for p, d in zip(provincias.index, provincias["deducida"])],
    "valor": provincias[perfil].to_numpy(),
})
tabla["nivel"] = [estilo.categoria_vs_pais(v, valor_pais) for v in tabla["valor"]]
tabla["categoria"] = [etiquetas_cat[n] for n in tabla["nivel"]]
tabla["color"] = [estilo.CATEGORIAS_VS_PAIS[n][1] for n in tabla["nivel"]]
tabla["valor_txt"] = [pct(v) for v in tabla["valor"]]

# --- Mapa y ranking ----------------------------------------------------------
col_mapa, col_ranking = st.columns([5, 6], gap="medium")

with col_mapa, ui.tarjeta("mapa"):
    ui.titulo_tarjeta("¿Dónde está por encima del país?", f"{perfil} · país {pct(valor_pais)}")
    graficos.mostrar(
        graficos.mapa(tabla, datos.geojson(), seleccion, perfil),
        key="mapa", on_select="rerun", selection_mode="points",
    )
    ui.referencias_mapa()

with col_ranking, ui.tarjeta("ranking"):
    ui.titulo_tarjeta(f"% de estudiantes en {perfil}", "Arriba de la barra gris, más que el país; abajo, menos.")
    ui.referencias([("barrita", estilo.COLOR_COMPARACION[perfil], "Provincia"),
                    ("barrita", estilo.COLOR_PAIS, "Todo el país")])
    graficos.mostrar(
        graficos.ranking(tabla, valor_pais, seleccion, perfil),
        key="ranking", on_select="rerun", selection_mode="points",
    )

# --- Detalle de la provincia elegida ----------------------------------------------
with ui.tarjeta("detalle"):
    izq, der = st.columns([3, 2], vertical_alignment="bottom")
    der.selectbox("Provincia", provincias.index, key="provincia")
    seleccion = st.session_state["provincia"]
    info = provincias.loc[seleccion]
    accion = acciones.loc[seleccion]
    with izq:
        st.subheader(seleccion + ("*" if info["deducida"] else ""))
        st.caption(f"{ui.miles(info['estudiantes'])} estudiantes · {ui.num(info['respuestas'], 0)} respuestas")

    c_dato, c_mezcla, c_edad = st.columns(3, gap="medium")

    with c_dato:
        nivel = estilo.categoria_vs_pais(info[perfil], valor_pais)
        cuadrito = estilo.CATEGORIAS_VS_PAIS[nivel][1]
        por_que = ""
        if accion["perfil_prioritario"] and not pd.isna(accion["perfil_prioritario"]):
            por_que = (f'<span class="texto">Porque es donde {escape(seleccion)} más supera al país: '
                       f'{escape(accion["perfil_prioritario"])} (+{ui.num(accion["exceso_pct"], 0)}%).</span>')
        st.html(
            f'<div class="dss-caja dato"><span class="chico">{escape(perfil)}</span>'
            f'<span class="grande">{pct(info[perfil])}</span>'
            f'<span class="texto"><span class="dss-cuadrito" style="background:{cuadrito}"></span> '
            f'{COMPARACION[nivel]} (país {pct(valor_pais)})</span></div>'
            f'<div style="height:14px"></div>'
            f'<div class="dss-caja accion"><span class="chico">Acción sugerida</span>'
            f'<span class="accion-titulo">{escape(accion["accion"])}</span>'
            f'<span class="texto">{escape(accion["cuando"])}</span>{por_que}</div>'
        )

    with c_mezcla:
        ui.titulo_tarjeta(f"¿Cómo se reparte {seleccion}?", "Cada barra suma 100%. Abajo, el país.")
        mezcla = pd.DataFrame([info[estilo.PERFILES], pais[estilo.PERFILES]])
        graficos.mostrar(graficos.barras_apiladas(mezcla, [seleccion, "País"], alto_fila=56))
        ui.referencias([("punto", estilo.COLOR_PERFIL[p], p) for p in estilo.PERFILES])

    with c_edad:
        ui.titulo_tarjeta(f"{perfil} por edad", f"% de cada edad en este perfil")
        ui.referencias([("barrita", estilo.COLOR_COMPARACION[perfil], seleccion),
                        ("barrita", estilo.COLOR_PAIS, "País")])
        filas = por_prov_edad[por_prov_edad["provincia"] == seleccion].set_index("edad")
        graficos.mostrar(graficos.columnas_contra_pais(
            [str(e) for e in filas.index], filas[perfil].tolist(), edad_pais.loc[filas.index, perfil].tolist(),
            perfil, seleccion, titulo_x="Edad (años)",
        ))

ui.nota("* Nombre de provincia deducido del código del dataset: falta confirmarlo con el informe oficial. "
        "Contornos de las provincias: Natural Earth (dominio público).")
