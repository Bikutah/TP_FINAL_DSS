"""Colores y estilo de los gráficos (tema cálido y amigable).

Todos los colores de la app salen de acá. Si un gráfico necesita un color,
se importa de este módulo en vez de escribir el código del color a mano.

Para que Plotly use este estilo y no el de Streamlit:
    st.plotly_chart(fig, theme=None)
"""

import plotly.graph_objects as go
import plotly.io as pio

# --- Base ---------------------------------------------------------------
FONDO = "#FBF7F1"
TARJETA = "#FFFFFF"
TEXTO = "#2B2118"
TEXTO_SUAVE = "#6E5F50"
ACENTO = "#2F6F5E"
LINEA_EJE = "#CDBFAE"
GRILLA = "#EFE7DC"
LINEA_PAIS = "#2B2118"  # la marca del total del país en las barras

# --- Perfiles -------------------------------------------------------------
# Orden fijo. El color sigue al perfil, nunca a su posición en un ranking.
PERFILES = [
    "Sin problemáticas marcadas",
    "Alcohol sin borracheras",
    "Consumo de riesgo",
    "Malestar emocional",
    "Violencia entre pares",
]

# color: barras y mapa | tono: texto del perfil (pasa contraste) | tinte: fondo de tarjeta
COLOR_PERFIL = dict(zip(PERFILES, ["#D9CFC2", "#EBB548", "#B84A33", "#6B4E9B", "#5FA8C6"]))
TONO_PERFIL = dict(zip(PERFILES, ["#6E5F50", "#8A5E0B", "#9E3B27", "#5A3F88", "#2D6F8C"]))
TINTE_PERFIL = dict(zip(PERFILES, ["#F1ECE5", "#FBF0D9", "#F8E1D8", "#ECE6F3", "#E2EFF5"]))
# Texto que va arriba de cada color (por ejemplo, el % dentro de una barra apilada)
TEXTO_SOBRE_PERFIL = dict(zip(PERFILES, ["#2B2118", "#2B2118", "#FFFFFF", "#FFFFFF", "#2B2118"]))

# --- Escala divergente: provincia contra el país ------------------------
# Se mide en % del valor del país: (provincia - país) / país.
# Los cortes de 5% coinciden con la regla de acción de src/reglas.py.
CATEGORIAS_VS_PAIS = [
    ("15% o más por encima del país", "#B4532A"),
    ("Entre 5% y 15% por encima", "#E99A70"),
    ("Parecido al país (±5%)", "#E9E2D8"),
    ("Entre 5% y 15% por debajo", "#86B2D2"),
    ("15% o más por debajo del país", "#3D7AA5"),
]


def categoria_vs_pais(valor: float, pais: float) -> int:
    """Devuelve la posición (0 a 4) en CATEGORIAS_VS_PAIS."""
    r = (valor - pais) / pais
    if r >= 0.15:
        return 0
    if r >= 0.05:
        return 1
    if r > -0.05:
        return 2
    if r > -0.15:
        return 3
    return 4


# --- Plantilla de Plotly ------------------------------------------------
pio.templates["calido"] = go.layout.Template(
    layout=dict(
        font=dict(family="Nunito Sans, system-ui, sans-serif", color=TEXTO, size=14),
        title=dict(font=dict(family="Nunito, system-ui, sans-serif", size=18, color=TEXTO)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=[COLOR_PERFIL[p] for p in PERFILES],
        xaxis=dict(gridcolor=GRILLA, linecolor=LINEA_EJE, zeroline=False, ticks="", automargin=True),
        yaxis=dict(gridcolor=GRILLA, linecolor=LINEA_EJE, zeroline=False, ticks="", automargin=True),
        hoverlabel=dict(bgcolor=TARJETA, bordercolor=LINEA_EJE, font=dict(color=TEXTO)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
        margin=dict(l=8, r=8, t=40, b=8),
        bargap=0.3,
        separators=",.",  # coma decimal y punto de miles, como en Argentina
    )
)
pio.templates.default = "calido"
