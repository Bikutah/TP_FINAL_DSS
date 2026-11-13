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
def barras_vector_promedio(filas: pd.DataFrame, perfil: str, margen_izq: int = 250) -> go.Figure:
    """Barras del vector de promedios del perfil con una marca en el total del país."""
    color = estilo.COLOR_PERFIL[perfil]
    fig = go.Figure()
    fig.add_bar(
        x=filas[perfil], y=filas["descripcion"], orientation="h", name=perfil,
        marker=dict(color=color, cornerradius=5),
        text=[pct(v, 0) for v in filas[perfil]], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO, size=13),
        customdata=[[pct(a), pct(b)] for a, b in zip(filas[perfil], filas["Total país"])],
        hovertemplate="<b>%{y}</b><br>Perfil: %{customdata[0]}<br>País: %{customdata[1]}<extra></extra>",
    )
    fig.add_scatter(
        x=filas["Total país"], y=filas["descripcion"], mode="markers", name="Total del país",
        marker=dict(symbol="line-ns-open", size=26, color=estilo.LINEA_PAIS, line=dict(width=3, color=estilo.LINEA_PAIS)),
        hoverinfo="skip",
    )
    fig.update_layout(
        showlegend=False, bargap=0.38, height=38 * len(filas) + 16,
        margin=dict(l=margen_izq, r=48, t=4, b=4),
    )
    fig.update_yaxes(autorange="reversed", automargin=False, showgrid=False, showline=False,
                     tickfont=dict(size=14))
    fig.update_xaxes(range=[0, 100])
    _sin_ejes(fig)
    return fig


def barras_verticales(etiquetas: list[str], valores: list[float], color: str,
                      pais: list[float] | None = None, alto: int = 240, titulo_x: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=etiquetas, y=valores, marker=dict(color=color, cornerradius=5),
        text=[pct(v, 0) for v in valores], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO, size=13),
        customdata=[pct(v) for v in valores],
        hovertemplate=f"<b>{titulo_x} %{{x}}</b>: %{{customdata}}<extra></extra>",
    )
    tope = max(valores)
    if pais is not None:
        tope = max(tope, max(pais))
        fig.add_scatter(
            x=etiquetas, y=pais, mode="markers", name="País",
            marker=dict(symbol="line-ew-open", size=34, color=estilo.LINEA_PAIS, line=dict(width=3, color=estilo.LINEA_PAIS)),
            customdata=[pct(v) for v in pais], hovertemplate="País: %{customdata}<extra></extra>",
        )
    fig.update_layout(showlegend=False, bargap=0.35, height=alto, margin=dict(l=4, r=4, t=24, b=4))
    fig.update_yaxes(visible=False, range=[0, tope * 1.18], fixedrange=True)
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


def ranking(df: pd.DataFrame, valor_pais: float, seleccion: str) -> go.Figure:
    """Barras horizontales ordenadas, con una línea en el valor del país.

    df (ya ordenado): provincia, etiqueta, valor, color.
    """
    elegida = df["provincia"] == seleccion
    fig = go.Figure()
    fig.add_bar(
        x=df["valor"], y=df["etiqueta"], orientation="h",
        marker=dict(color=df["color"], cornerradius=4,
                    line=dict(color=[estilo.TEXTO if e else "rgba(0,0,0,0)" for e in elegida], width=2)),
        text=[pct(v) for v in df["valor"]], textposition="outside", cliponaxis=False,
        textfont=dict(color=estilo.TEXTO, size=12),
        customdata=df["provincia"],
        hovertemplate="<b>%{customdata}</b>: %{x:.1f}%<extra></extra>",
    )
    fig.add_vline(x=valor_pais, line=dict(color=estilo.LINEA_PAIS, width=2))
    fig.add_annotation(x=valor_pais, y=1, yref="paper", yanchor="bottom", showarrow=False,
                       text=f"País {pct(valor_pais)}", font=dict(size=12, color=estilo.TEXTO))
    etiquetas = [f"<b>{t}</b>" if e else t for t, e in zip(df["etiqueta"], elegida)]
    fig.update_yaxes(autorange="reversed", showgrid=False, showline=False,
                     tickvals=df["etiqueta"], ticktext=etiquetas, tickfont=dict(size=13))
    fig.update_xaxes(range=[0, df["valor"].max() * 1.15])
    fig.update_layout(showlegend=False, bargap=0.3, height=26 * len(df) + 40, margin=dict(l=8, r=8, t=26, b=4))
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
