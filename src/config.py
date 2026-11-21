"""Configuración del pipeline: rutas, variables del modelo y parámetros.

Todo lo que se puede cambiar del modelo está acá. Si cambia algo, se vuelve a
correr `python scripts/entrenar.py` y la app muestra los resultados nuevos.
"""

from pathlib import Path

# --- Rutas ------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parents[1]
RUTA_DATOS = RAIZ / "data" / "raw" / "data_set.csv"
CARPETA_ARTEFACTOS = RAIZ / "artefactos"

# --- Indicadores que entran al k-means ---------------------------------------
# nombre -> (columna qn de la EMSE, descripción, dimensión)
# Las columnas qn ya vienen dicotomizadas: 1 = sí, 2 = no.
VARIABLES_MODELO = {
    "soledad": ("qn22", "Se sintió solo casi siempre", "Salud mental"),
    "preocupacion": ("qn23", "La preocupación no lo deja dormir", "Salud mental"),
    "ideacion": ("qn24", "Pensó seriamente en el suicidio", "Salud mental"),
    "plan": ("qn25", "Hizo un plan de suicidio", "Salud mental"),
    "intento": ("qn26", "Intentó suicidarse", "Salud mental"),
    "atacado": ("qn15", "Fue atacado físicamente", "Violencia"),
    "peleas": ("qn16", "Participó en peleas", "Violencia"),
    "bullying_escuela": ("qn66", "Bullying en la escuela", "Violencia"),
    "bullying_fuera": ("qn67", "Bullying fuera de la escuela", "Violencia"),
    "ciberacoso": ("qn68", "Ciberacoso", "Violencia"),
    "tabaco": ("qn29", "Fuma tabaco", "Consumo"),
    "alcohol": ("qn35", "Toma alcohol", "Consumo"),
    "borrachera": ("qn38", "Se emborrachó alguna vez", "Consumo"),
    "marihuana": ("qn42", "Consume marihuana", "Consumo"),
    "falta_clases": ("qn53", "Faltó a clases sin permiso", "Escuela"),
}
COLUMNAS_MODELO = list(VARIABLES_MODELO)

# --- Variables que NO entran al modelo y se usan para describir los grupos ---
# nombre -> (columna, valor que cuenta como "sí", descripción)
VARIABLES_CONTEXTO = {
    "padres_no_comprenden": ("qn56", 2, "Padres no suelen entenderlo"),
    "sin_amigos": ("qn27", 1, "No tiene amigos cercanos"),
    "hambre": ("qn6", 1, "Pasa hambre por falta de comida"),
}

# --- Provincias: dígitos 5 y 6 de stratum, en orden alfabético -----------------
PROVINCIAS = {
    "01": "Buenos Aires", "02": "Catamarca", "03": "Chaco", "04": "Chubut", "05": "CABA",
    "06": "Córdoba", "07": "Corrientes", "08": "Entre Ríos", "09": "Formosa", "10": "Jujuy",
    "11": "La Pampa", "12": "La Rioja", "13": "Mendoza", "14": "Misiones", "15": "Neuquén",
    "16": "Río Negro", "17": "Salta", "18": "San Juan", "19": "San Luis", "20": "Santa Cruz",
    "21": "Santa Fe", "22": "Santiago del Estero", "23": "Tierra del Fuego", "24": "Tucumán",
}
# Sin archivo propio en la OMS: el nombre se deduce del orden (hay que confirmarlo)
PROVINCIAS_DEDUCIDAS = {"05", "09", "11", "15", "16", "19"}

# q1: 3 = 13 años ... 7 = 17 años · q2: 1 = varón, 2 = mujer
EDAD_POR_CODIGO = {3: 13, 4: 14, 5: 15, 6: 16, 7: 17}
SEXO_POR_CODIGO = {1: "Varón", 2: "Mujer"}

# --- Parámetros del modelo ----------------------------------------------------
K = 5                      # cantidad de perfiles (elegida con el codo y el dendrograma)
SEMILLAS = range(8)        # se entrena con 8 semillas y se queda la de menor inercia
N_INIT = 50                # arranques por semilla
K_CODO = range(1, 11)      # k que se prueban en el método del codo
N_INIT_CODO = 10
SEMILLA = 0                # semilla de las muestras (silueta y dendrograma)
MUESTRA_SILUETA = 6000
MUESTRA_DENDROGRAMA = 4000
HOJAS_DENDROGRAMA = 30     # el dendrograma se muestra con las últimas 30 uniones
