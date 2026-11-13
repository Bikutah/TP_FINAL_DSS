"""Piezas de interfaz reutilizables (HTML con las clases de estilo.css)."""

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from componentes import estilo

RUTA_CSS = Path(__file__).with_name("estilo.css")


def aplicar_estilo():
    st.html(RUTA_CSS)


# --- Números en formato argentino ---------------------------------------------
def num(valor: float, decimales: int = 1) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(valor: float, decimales: int = 1) -> str:
    return num(valor, decimales) + "%"


def miles(valor: float) -> str:
    return f"≈ {num(valor / 1000, 0)} mil"


def millones(valor: float) -> str:
    return f"{num(valor / 1e6, 1)} millones"


# --- Piezas -----------------------------------------------------------------
def encabezado(titulo: str, bajada: str):
    st.title(titulo)
    st.html(f'<p class="dss-bajada">{escape(bajada)}</p>')


def tarjeta(nombre: str):
    """Contenedor blanco con bordes redondeados (ver estilo.css)."""
    return st.container(key=f"tarjeta_{nombre}")


def titulo_tarjeta(titulo: str, subtitulo: str = ""):
    sub = f'<p class="dss-s">{escape(subtitulo)}</p>' if subtitulo else ""
    st.html(f'<h3 class="dss-t">{escape(titulo)}</h3>{sub}')


def kpis(items: list[tuple[str, str]]):
    bloques = "".join(
        f'<div class="dss-kpi"><span class="valor">{escape(v)}</span><span class="texto">{escape(t)}</span></div>'
        for v, t in items
    )
    st.html(f'<section class="dss-kpis" aria-label="Datos generales">{bloques}</section>')


def tarjetas_perfiles(perfiles: pd.DataFrame):
    bloques = []
    for _, fila in perfiles.iterrows():
        p = fila["perfil"]
        tono, tinte = estilo.TONO_PERFIL[p], estilo.TINTE_PERFIL[p]
        bloques.append(
            f'<article class="dss-perfil" style="background:{tinte}">'
            f'<span class="pct" style="color:{tono}">{pct(fila["pct"])}</span>'
            f'<span class="nombre">{escape(p)}</span>'
            f'<span class="desc">{escape(fila["descripcion"])}</span>'
            f'<span class="estim">{miles(fila["estudiantes_estimados"])} estudiantes</span>'
            f'<span class="dss-chip" style="color:{tono}">{escape(fila["accion"])}</span>'
            "</article>"
        )
    st.html(f'<div class="dss-perfiles">{"".join(bloques)}</div>')


ICONO_TENDENCIA = '<span style="color:#FFFFFF;font-size:1.3rem;font-weight:800">↗</span>'


def callout(destacado: str, resto: str):
    st.html(
        f'<div class="dss-callout"><span class="icono" aria-hidden="true">{ICONO_TENDENCIA}</span>'
        f"<p style=\"margin:0\"><strong>{escape(destacado)}</strong> {escape(resto)}</p></div>"
    )


def referencias(items: list[tuple[str, str, str]]):
    """items: (forma, color, texto). forma: punto, barrita, cuadrito o rayita."""
    partes = []
    for forma, color, texto in items:
        fondo = f' style="background:{color}"' if forma != "rayita" else ""
        partes.append(f'<span class="dss-ref"><span class="dss-{forma}"{fondo} aria-hidden="true"></span>{escape(texto)}</span>')
    st.html(f'<div class="dss-refs">{"".join(partes)}</div>')


def referencias_mapa():
    """Referencias de la escala divergente, una debajo de la otra."""
    partes = "".join(
        f'<span class="dss-ref"><span class="dss-cuadrito" style="background:{color}" aria-hidden="true"></span>'
        f"{escape(texto)}</span>"
        for texto, color in estilo.CATEGORIAS_VS_PAIS
    )
    st.html(f'<div class="dss-refs" style="flex-direction:column">{partes}</div>')


def nota(texto: str):
    st.html(f'<p class="dss-nota">{escape(texto)}</p>')
