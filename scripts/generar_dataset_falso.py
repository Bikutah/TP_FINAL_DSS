"""Genera un dataset FALSO con el mismo formato que data_set.csv de la EMSE 2018.

Sirve para probar el pipeline y la app sin los datos reales, y para ver que la
app cambia cuando cambian los datos. Los números que salen NO son reales.

Desde la carpeta del repo:
    python scripts/generar_dataset_falso.py
    python scripts/entrenar.py --datos data/ejemplo/data_set_falso.csv

Cómo se arma: cada estudiante inventado pertenece a uno de 5 perfiles "escondidos"
y responde las preguntas con las probabilidades de ese perfil. Las proporciones de
perfiles son distintas a las reales a propósito (más consumo de riesgo), y cambian
con la edad, el sexo y la provincia. Después se mezclan con ruido y algunas
respuestas vacías, como en una encuesta de verdad.
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "data" / "ejemplo" / "data_set_falso.csv"
N = 20_000
SEMILLA = 42

PERFILES = ["sin", "alcohol", "riesgo", "malestar", "violencia"]
# Proporciones base del país inventado (las reales son 37 / 16 / 22 / 13 / 11)
BASE = np.array([0.28, 0.18, 0.27, 0.14, 0.13])

# Probabilidad de responder "sí" a cada pregunta según el perfil escondido
PREGUNTAS = {  # columna: [sin, alcohol, riesgo, malestar, violencia]
    "qn22": [0.08, 0.07, 0.11, 0.59, 0.22],  # soledad
    "qn23": [0.06, 0.07, 0.09, 0.44, 0.17],  # preocupación
    "qn24": [0.09, 0.08, 0.09, 0.96, 0.17],  # ideación
    "qn25": [0.05, 0.05, 0.06, 0.87, 0.09],  # plan
    "qn26": [0.05, 0.04, 0.05, 0.75, 0.07],  # intento
    "qn15": [0.08, 0.12, 0.15, 0.42, 0.25],  # atacado
    "qn16": [0.12, 0.19, 0.34, 0.40, 0.26],  # peleas
    "qn66": [0.11, 0.09, 0.08, 0.39, 0.80],  # bullying en la escuela
    "qn67": [0.04, 0.08, 0.14, 0.42, 0.84],  # bullying fuera
    "qn68": [0.05, 0.09, 0.15, 0.47, 0.74],  # ciberacoso
    "qn29": [0.02, 0.11, 0.38, 0.42, 0.15],  # tabaco
    "qn35": [0.01, 0.99, 0.96, 0.74, 0.55],  # alcohol
    "qn38": [0.08, 0.01, 0.99, 0.62, 0.37],  # borrachera
    "qn42": [0.01, 0.02, 0.22, 0.19, 0.05],  # marihuana
    "qn53": [0.19, 0.24, 0.39, 0.41, 0.32],  # faltó a clases
}
CONTEXTO = {  # columna: (valor que cuenta como "sí", probabilidades por perfil)
    "qn56": (2, [0.49, 0.54, 0.61, 0.81, 0.62]),  # padres no suelen entenderlo
    "qn27": (1, [0.06, 0.03, 0.03, 0.09, 0.05]),  # sin amigos cercanos
    "qn6": (1, [0.012, 0.010, 0.011, 0.056, 0.019]),  # hambre
}
PROB_VACIO = 0.011  # deja ~15% de filas con alguna respuesta vacía, como en la EMSE


def main():
    rng = np.random.default_rng(SEMILLA)

    provincia = rng.integers(1, 25, size=N)
    edad = rng.integers(13, 18, size=N)
    sexo = rng.integers(1, 3, size=N)  # 1 = varón, 2 = mujer

    # Cada provincia tiene su propia mezcla de perfiles
    efecto_provincia = rng.lognormal(0, 0.3, size=(25, 5))

    perfil = np.empty(N, dtype=int)
    for i in range(N):
        p = BASE.copy()
        p[0] *= 1.5 - 0.25 * (edad[i] - 13)  # "baja prevalencia" baja con la edad
        p[2] *= 0.3 + 0.45 * (edad[i] - 13)  # consumo de riesgo sube con la edad
        p[3] *= 1.6 if sexo[i] == 2 else 0.5  # malestar emocional, más en mujeres
        p *= efecto_provincia[provincia[i]]
        perfil[i] = rng.choice(5, p=p / p.sum())

    datos = pd.DataFrame({
        "site": "FALSO",
        "record": np.arange(1, N + 1),
        "q1": edad - 10,  # q1: 3 = 13 años ... 7 = 17 años
        "q2": sexo,
        "stratum": [int(f"2018{p:02d}{rng.integers(1, 40):03d}") for p in provincia],
        "psu": rng.integers(1, 60, size=N),
        "weight": np.round(rng.lognormal(3.3, 0.8, size=N), 4),
    })
    for columna, probs in PREGUNTAS.items():
        si = rng.random(N) < np.array(probs)[perfil]
        datos[columna] = np.where(si, 1.0, 2.0)
    for columna, (valor_si, probs) in CONTEXTO.items():
        si = rng.random(N) < np.array(probs)[perfil]
        datos[columna] = np.where(si, float(valor_si), float(3 - valor_si))

    # Respuestas vacías y algunos estudiantes fuera de 13 a 17 años
    for columna in list(PREGUNTAS) + list(CONTEXTO):
        datos.loc[rng.random(N) < PROB_VACIO, columna] = np.nan
    fuera = rng.random(N) < 0.01
    datos.loc[fuera, "q1"] = rng.choice([1, 2, 8], size=fuera.sum())

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(SALIDA, index=False)
    reparto = pd.Series(perfil).map(dict(enumerate(PERFILES))).value_counts(normalize=True).mul(100).round(1)
    print(f"Guardado {SALIDA.relative_to(RAIZ)}: {N:,} estudiantes inventados".replace(",", "."))
    print("Perfiles escondidos (sin pesos):", reparto.to_dict())


if __name__ == "__main__":
    main()
