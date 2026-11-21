"""Gestión del conocimiento: nombre de cada perfil y acción sugerida por provincia.

Son reglas escritas por el grupo a partir de leer los centroides. No las aprende
el modelo: el k-means encuentra los grupos y estas reglas los interpretan.
"""

import pandas as pd

# Orden fijo en el que se muestran los perfiles en toda la app
PERFILES = [
    "Baja prevalencia de problemáticas",
    "Alcohol sin borracheras",
    "Consumo de riesgo",
    "Malestar emocional",
    "Violencia entre pares",
]

DESCRIPCION = {
    "Baja prevalencia de problemáticas": "Bajo en todos los indicadores",
    "Alcohol sin borracheras": "Toma alcohol, nunca se emborrachó",
    "Consumo de riesgo": "Borracheras, tabaco y marihuana",
    "Malestar emocional": "Ideación suicida, soledad, bullying",
    "Violencia entre pares": "Bullying y ciberacoso",
}

# perfil -> (acción, a quién / cuándo)
ACCIONES = {
    "Baja prevalencia de problemáticas": ("Sin acción", ""),
    "Alcohol sin borracheras": ("Prevención de consumo", "En 1.º y 2.º año, antes del salto de los 15."),
    "Consumo de riesgo": ("Prevención de consumo", "En 1.º y 2.º año, antes del salto de los 15."),
    "Malestar emocional": ("Salud mental y contención", "En todos los años, con foco en mujeres y en la familia."),
    "Violencia entre pares": ("Convivencia escolar y bullying", "En todos los años."),
}

# Una provincia tiene prioridad si supera al país en más de este porcentaje
UMBRAL_PRIORIDAD = 0.05


def nombrar(centroide: pd.Series) -> str:
    """Nombre del perfil según su centroide (proporción de 'sí' en cada indicador).

    Se nombra por reglas y no por el número de grupo, porque el k-means numera
    los grupos de cualquier forma y cambia si se reentrena.
    """
    if centroide["ideacion"] > 0.5:
        return "Malestar emocional"
    if centroide["bullying_fuera"] > 0.5:
        return "Violencia entre pares"
    if centroide["alcohol"] > 0.5 and centroide["borrachera"] > 0.5:
        return "Consumo de riesgo"
    if centroide["alcohol"] > 0.5:
        return "Alcohol sin borracheras"
    return "Baja prevalencia de problemáticas"


def accion_sugerida(pct_provincia: pd.Series, pct_pais: pd.Series) -> dict:
    """Acción para una provincia según el perfil problemático en el que más supera al país."""
    problematicos = [p for p in PERFILES if p != "Baja prevalencia de problemáticas"]
    exceso = {p: (pct_provincia[p] - pct_pais[p]) / pct_pais[p] for p in problematicos}
    perfil = max(exceso, key=exceso.get)
    if exceso[perfil] <= UMBRAL_PRIORIDAD:
        return {"perfil_prioritario": "", "exceso_pct": round(100 * exceso[perfil], 1),
                "accion": "Sin prioridad marcada",
                "cuando": f"Ningún perfil supera al país en más de {UMBRAL_PRIORIDAD:.0%}."}
    accion, cuando = ACCIONES[perfil]
    return {"perfil_prioritario": perfil, "exceso_pct": round(100 * exceso[perfil], 1),
            "accion": accion, "cuando": cuando}
