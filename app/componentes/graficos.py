"""Gráficos de la app (Plotly). Solo los tipos del apunte: barras, mapa, codo y dendrograma."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from componentes import estilo
from componentes.ui import num, pct

# Sin barra de herramientas y con el mapa base servido por la app (anda sin internet)
CONFIG = {"displayModeBar": False, "scrollZoom": False, "topojsonURL": "/app/static/"}


def mostrar(fig: go.Figure, **kwargs):
    """Dibuja con nuestra plantilla (theme=None) y sin barra de herramientas."""
    return st.plotly_chart(fig, theme=None, config=CONFIG, **kwargs)


def _sin_ejes(fig: go.Figure):
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(fixedrange=True)


# --- Resumen ---------------------------------------------------------------
def barras_apiladas(tabla: pd.DataFrame, etiquetas: list[str], alto_fila: int = 44) -> go.Figure:
    """Una barra por fila de `tabla` (que suma 100%), con un segmento por perfil."""
    fig = go.Figure()
    for p in estilo.PERFILES:
        valores = tabla[p].tolist()
        fig.add_bar(
            x=valores, y=etiquetas, orientation="h", name=p,
            marker=dict(color=estilo.COLOR_PERFIL[p], line=dict(color=estilo.TARJETA, width=2)),
            text=[pct(v, 0) if v >= 7 else "" for v in valores], textposition="inside",
            insidetextanchor="middle", textangle=0, textfont=dict(color=estilo.TEXTO_SOBRE_PERFIL[p], size=12),
            customdata=[pct(v) for v in valores],
            hovertemplate=f"<b>%{{y}}</b><br>{p}: %{{customdata}}<extra></extra>",
        )
    fig.update_layout(
        barmode="stack", bargap=0.28, showlegend=False,
        height=alto_fila * len(etiquetas) + 20, margin=dict(l=8, r=8, t=4, b=4),
        uniformtext=dict(minsize=10, mode="hide"),
    )
    fig.update_yaxes(autorange="reversed", showgrid=False, showline=False)
    fig.update_xaxes(range=[0, 100.5])
    _sin_ejes(fig)
    return fig


# --- Perfiles --------------------------------------------------------------
def barras_contra_pais(etiquetas: list[str], valores: list[float], pais: list[float], nombre: str,
                       margen_izq: int = 250, mostrar_escala: bool = False) -> go.Figure:
    """Dos barras por pregunta: el perfil (en su color) y todo el país (en gris), cada una con su número."""
    color = estilo.COLOR_COMPARACION[nombre] if nombre in estilo.COLOR_COMPARACION else estilo.ACENTO
    fig = go.Figure()
    fig.add_bar(
        x=valores, y=etiquetas, orientation="h", name=nombre,
        marker=dict(color=color, cornerradius=3),
        text=[f"<b>{pct(v, 0)}</b>" for v in valores], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO, size=13),
        customdata=[pct(v) for v in valores], hovertemplate=f"<b>%{{y}}</b><br>{nombre}: %{{customdata}}<extra></extra>",
    )
    fig.add_bar(
        x=pais, y=etiquetas, orientation="h", name="Todo el país",
        marker=dict(color=estilo.COLOR_PAIS, cornerradius=3),
        text=[pct(v, 0) for v in pais], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO_SUAVE, size=12),
        customdata=[pct(v) for v in pais], hovertemplate="<b>%{y}</b><br>Todo el país: %{customdata}<extra></extra>",
    )
    alto = 50 * len(etiquetas) + (30 if mostrar_escala else 8)
    fig.update_layout(showlegend=False, barmode="group", bargap=0.28, bargroupgap=0.12, height=alto,
                      margin=dict(l=margen_izq, r=44, t=4, b=26 if mostrar_escala else 4))
    fig.update_yaxes(autorange="reversed", automargin=False, showgrid=False, tickfont=dict(size=14),
                     ticklabelstandoff=10, showline=True, linecolor=estilo.LINEA_EJE, fixedrange=True)
    fig.update_xaxes(range=[0, 100], tickvals=[0, 25, 50, 75, 100], ticksuffix="%", showgrid=True,
                     gridcolor=estilo.GRILLA, showline=False, showticklabels=mostrar_escala,
                     tickfont=dict(size=12, color=estilo.TEXTO_SUAVE), fixedrange=True)
    return fig


def columnas_contra_pais(etiquetas: list[str], valores: list[float], pais: list[float], nombre: str,
                         nombre_valores: str, alto: int = 250, titulo_x: str = "") -> go.Figure:
    """Barras verticales de a pares: el lugar elegido (en color) y el país (en gris)."""
    color = estilo.COLOR_COMPARACION.get(nombre, estilo.ACENTO)
    fig = go.Figure()
    fig.add_bar(
        x=etiquetas, y=valores, name=nombre_valores, marker=dict(color=color, cornerradius=3),
        text=[f"<b>{pct(v, 0)}</b>" for v in valores], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO, size=12),
        customdata=[pct(v) for v in valores],
        hovertemplate=f"{titulo_x} %{{x}} · {nombre_valores}: %{{customdata}}<extra></extra>",
    )
    fig.add_bar(
        x=etiquetas, y=pais, name="País", marker=dict(color=estilo.COLOR_PAIS, cornerradius=3),
        text=[pct(v, 0) for v in pais], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO_SUAVE, size=12),
        customdata=[pct(v) for v in pais], hovertemplate=f"{titulo_x} %{{x}} · País: %{{customdata}}<extra></extra>",
    )
    tope = max(max(valores), max(pais))
    fig.update_layout(showlegend=False, barmode="group", bargap=0.3, bargroupgap=0.08, height=alto,
                      margin=dict(l=4, r=4, t=20, b=4))
    fig.update_yaxes(visible=False, range=[0, tope * 1.15], fixedrange=True)
    fig.update_xaxes(showline=True, linecolor=estilo.LINEA_EJE, showgrid=False, fixedrange=True,
                     type="category", title_text=titulo_x, title_font=dict(size=13, color=estilo.TEXTO_SUAVE))
    return fig


def barras_verticales(etiquetas: list[str], valores: list[float], color: str,
                      pais: list[float] | None = None, alto: int = 240, titulo_x: str = "") -> go.Figure:
    """Barras verticales (por edad). Los números van en una fila fija arriba, para no pisar la marca del país."""
    fig = go.Figure()
    fig.add_bar(
        x=etiquetas, y=valores, marker=dict(color=color, cornerradius=4),
        customdata=[pct(v) for v in valores],
        hovertemplate=f"<b>{titulo_x} %{{x}}</b>: %{{customdata}}<extra></extra>",
    )
    tope = max(valores)
    if pais is not None:
        tope = max(tope, max(pais))
        fig.add_scatter(
            x=etiquetas, y=pais, mode="markers", name="País",
            marker=dict(symbol="line-ew-open", size=30, color=estilo.LINEA_PAIS, line=dict(width=2.5, color=estilo.LINEA_PAIS)),
            customdata=[pct(v) for v in pais], hovertemplate="País: %{customdata}<extra></extra>",
        )
        # Rótulo "país" sobre la raya que más sobresale de su barra
        i = max(range(len(pais)), key=lambda j: pais[j] - valores[j])
        fig.add_annotation(x=i, y=pais[i], yshift=8, yanchor="bottom", showarrow=False, text="país",
                           font=dict(size=12, color=estilo.TEXTO))
    # x = posición de la barra (0, 1, 2…): si se pasa "13" como texto, Plotly lo toma como posición 13
    for posicion, valor in enumerate(valores):
        fig.add_annotation(x=posicion, y=1, yref="paper", yanchor="bottom", showarrow=False,
                           text=f"<b>{pct(valor, 0)}</b>", font=dict(size=13, color=estilo.TEXTO))
    fig.update_layout(showlegend=False, bargap=0.35, height=alto, margin=dict(l=4, r=4, t=26, b=4))
    fig.update_yaxes(visible=False, range=[0, tope * 1.08], fixedrange=True)
    fig.update_xaxes(showline=True, linecolor=estilo.LINEA_EJE, showgrid=False, fixedrange=True,
                     type="category", title_text=titulo_x, title_font=dict(size=13, color=estilo.TEXTO_SUAVE))
    return fig


def barras_horizontales(etiquetas: list[str], valores: list[float], color: str, alto: int = 130) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=valores, y=etiquetas, orientation="h", marker=dict(color=color, cornerradius=5),
        text=[pct(v) for v in valores], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO, size=13), hoverinfo="skip",
    )
    fig.update_layout(showlegend=False, bargap=0.4, height=alto, margin=dict(l=70, r=50, t=4, b=4))
    fig.update_yaxes(autorange="reversed", showgrid=False, showline=False)
    fig.update_xaxes(range=[0, max(valores) * 1.05])
    _sin_ejes(fig)
    return fig


# --- Provincias ------------------------------------------------------------
def mapa(df: pd.DataFrame, geo: dict, seleccion: str, nombre_valor: str) -> go.Figure:
    """Mapa de provincias con la escala divergente contra el país.

    df: provincia, categoria (texto de estilo.CATEGORIAS_VS_PAIS) y valor_txt.
    """
    orden = [c for c, _ in estilo.CATEGORIAS_VS_PAIS]
    fig = px.choropleth(
        df, geojson=geo, locations="provincia", featureidkey="properties.provincia",
        color="categoria", color_discrete_map=dict(estilo.CATEGORIAS_VS_PAIS),
        category_orders={"categoria": orden}, custom_data=["valor_txt"],
    )
    fig.update_traces(hovertemplate=f"<b>%{{location}}</b><br>{nombre_valor}: %{{customdata[0]}}<extra></extra>")
    for traza in fig.data:
        elegida = [loc == seleccion for loc in traza.locations]
        traza.marker.line.width = [2.6 if e else 0.7 for e in elegida]
        traza.marker.line.color = [estilo.TEXTO if e else "#FFFFFF" for e in elegida]
    # Encuadre fijo de Argentina continental + Malvinas y Tierra del Fuego
    fig.update_geos(visible=False, projection_type="mercator", bgcolor="rgba(0,0,0,0)",
                    lonaxis_range=[-74, -53], lataxis_range=[-56, -21.5])
    fig.update_layout(height=560, margin=dict(l=0, r=0, t=0, b=0), dragmode=False, showlegend=False)
    return fig


def ranking(df: pd.DataFrame, valor_pais: float, seleccion: str, perfil: str) -> go.Figure:
    """Ranking de provincias con el país metido como una barra gris más.

    df: provincia, etiqueta y valor (sin ordenar). Las provincias que quedan arriba de
    la barra gris tienen más que el país; las de abajo, menos.
    """
    filas = pd.concat([
        df[["provincia", "etiqueta", "valor"]],
        pd.DataFrame([{"provincia": "", "etiqueta": "Todo el país", "valor": valor_pais}]),
    ]).sort_values("valor", ascending=False, kind="stable")
    es_pais = filas["provincia"] == ""
    elegida = filas["provincia"] == seleccion
    color = estilo.COLOR_COMPARACION.get(perfil, estilo.ACENTO)
    fig = go.Figure()
    fig.add_bar(
        x=filas["valor"], y=filas["etiqueta"], orientation="h",
        marker=dict(color=[estilo.COLOR_PAIS if p else color for p in es_pais], cornerradius=4,
                    line=dict(color=[estilo.TEXTO if e else "rgba(0,0,0,0)" for e in elegida], width=2)),
        customdata=[pct(v) for v in filas["valor"]],
        hovertemplate="<b>%{y}</b>: %{customdata}<extra></extra>",
    )
    for etiqueta, valor, e, p in zip(filas["etiqueta"], filas["valor"], elegida, es_pais):
        texto = f"<b>{pct(valor)}</b>" if (e or p) else pct(valor)
        fig.add_annotation(x=1, xref="paper", xanchor="left", xshift=10, y=etiqueta, yref="y", showarrow=False,
                           text=texto, font=dict(size=12, color=estilo.TEXTO))
    etiquetas = [f"<b>{t}</b>" if (e or p) else t for t, e, p in zip(filas["etiqueta"], elegida, es_pais)]
    fig.update_yaxes(autorange="reversed", showgrid=False, showline=True, linecolor=estilo.LINEA_EJE,
                     tickvals=filas["etiqueta"], ticktext=etiquetas, tickfont=dict(size=13), ticklabelstandoff=8)
    fig.update_xaxes(range=[0, filas["valor"].max() * 1.04])
    fig.update_layout(showlegend=False, bargap=0.3, height=26 * len(filas) + 16, margin=dict(l=8, r=58, t=4, b=4))
    _sin_ejes(fig)
    return fig


# --- Clasificar un estudiante -------------------------------------------------
def distancias(tabla: pd.DataFrame, ganador: str) -> go.Figure:
    """Distancia del estudiante a cada centroide. El perfil asignado va en color y el resto en gris."""
    es_ganador = tabla["perfil"] == ganador
    fig = go.Figure()
    fig.add_bar(
        x=tabla["distancia"], y=tabla["perfil"], orientation="h",
        marker=dict(color=[estilo.COLOR_COMPARACION[p] if g else estilo.COLOR_PAIS
                           for p, g in zip(tabla["perfil"], es_ganador)], cornerradius=4),
        text=[f"<b>{num(v, 2)}</b>" if g else num(v, 2) for v, g in zip(tabla["distancia"], es_ganador)],
        textposition="outside", cliponaxis=False, textfont=dict(color=estilo.TEXTO, size=13), hoverinfo="skip",
    )
    etiquetas = [f"<b>{p}</b>" if g else p for p, g in zip(tabla["perfil"], es_ganador)]
    fig.update_yaxes(autorange="reversed", showgrid=False, showline=True, linecolor=estilo.LINEA_EJE,
                     tickvals=tabla["perfil"], ticktext=etiquetas, tickfont=dict(size=14), ticklabelstandoff=8)
    fig.update_xaxes(range=[0, max(tabla["distancia"].max() * 1.15, 1)])
    fig.update_layout(showlegend=False, bargap=0.35, height=48 * len(tabla) + 16, margin=dict(l=8, r=50, t=4, b=4))
    _sin_ejes(fig)
    return fig


# --- Modelo ----------------------------------------------------------------
def codo(inercias: dict, k_elegido: int) -> go.Figure:
    ks = sorted(int(k) for k in inercias)
    valores = [inercias[str(k)] / 1e6 for k in ks]
    fig = go.Figure()
    fig.add_scatter(
        x=ks, y=valores, mode="lines+markers", line=dict(color=estilo.ACENTO, width=2),
        marker=dict(size=9, color="#FFFFFF", line=dict(color=estilo.ACENTO, width=2)),
        customdata=[num(v, 2) for v in valores],
        hovertemplate="k = %{x}: %{customdata} millones<extra></extra>",
    )
    y_elegido = inercias[str(k_elegido)] / 1e6
    fig.add_scatter(x=[k_elegido], y=[y_elegido], mode="markers", hoverinfo="skip",
                    marker=dict(size=15, color=estilo.ACENTO, line=dict(color="#FFFFFF", width=2)))
    fig.add_vline(x=k_elegido, line=dict(color=estilo.ACENTO, width=1, dash="dot"))
    fig.add_annotation(x=k_elegido, y=max(valores), text=f"<b>k = {k_elegido}</b>", showarrow=False,
                       xanchor="left", xshift=8, font=dict(color="#24584A", size=13))
    fig.update_layout(showlegend=False, height=300, margin=dict(l=8, r=8, t=8, b=8))
    fig.update_xaxes(title_text="Cantidad de grupos (k)", tickmode="linear", dtick=1, showgrid=False,
                     showline=True, fixedrange=True)
    fig.update_yaxes(title_text="Inercia (millones)", fixedrange=True)
    return fig


def dendrograma(icoord: list, dcoord: list, corte: float, k: int) -> go.Figure:
    xs, ys = [], []
    for ic, dc in zip(icoord, dcoord):
        xs += ic + [None]
        ys += dc + [None]
    fig = go.Figure()
    fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(color=estilo.TEXTO_SUAVE, width=1.5), hoverinfo="skip")
    fig.add_hline(y=corte, line=dict(color="#B84A33", width=2, dash="dash"))
    fig.add_annotation(x=1, xref="paper", y=corte, yanchor="bottom", xanchor="right", showarrow=False,
                       text=f"<b>corte: {k} grupos</b>", font=dict(color="#9E3B27", size=13))
    fig.update_layout(showlegend=False, height=300, margin=dict(l=8, r=8, t=8, b=8))
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(title_text="Distancia de unión", rangemode="tozero", fixedrange=True)
    return fig
