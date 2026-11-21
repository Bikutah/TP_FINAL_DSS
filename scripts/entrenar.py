"""Corre todo el pipeline y deja los resultados en artefactos/.

Desde la carpeta del repo:
    python scripts/entrenar.py
    python scripts/entrenar.py --datos data/ejemplo/data_set_falso.csv   (con el dataset falso)

Tarda unos minutos (entrena el k-means 8 veces con 50 arranques cada una).
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config, modelo, preprocesamiento, resultados  # noqa: E402
from src.reglas import PERFILES  # noqa: E402

# Lo que dieron las notebooks, para avisar si algo cambió
ESPERADO = {"Baja prevalencia de problemáticas": 37.1, "Alcohol sin borracheras": 16.1,
            "Consumo de riesgo": 22.4, "Malestar emocional": 13.3, "Violencia entre pares": 11.0}


def paso(texto: str):
    print(f"\n{texto}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Entrena el modelo y genera artefactos/")
    parser.add_argument("--datos", type=Path, default=config.RUTA_DATOS,
                        help="CSV con el formato de la EMSE (por defecto data/raw/data_set.csv)")
    args = parser.parse_args()
    ruta = args.datos if args.datos.is_absolute() else (Path.cwd() / args.datos)
    falso = "falso" in ruta.name.lower()
    inicio = time.time()

    paso(f"1/4 Cargando y preparando {ruta.name}…")
    if falso:
        print("    OJO: es el dataset FALSO. Los resultados no son reales.")
    prep = preprocesamiento.preprocesar(preprocesamiento.cargar(ruta))
    X, pesos = preprocesamiento.matriz_modelo(prep.completos)
    print(f"    {len(prep.base):,} estudiantes de 13 a 17 años · {len(X):,} con las 15 respuestas".replace(",", "."))

    paso("2/4 Entrenando (codo, silueta, k-means con 8 semillas y dendrograma)…")
    res_modelo = modelo.entrenar(X, pesos)
    estables = sum(s["ari"] >= 0.99 for s in res_modelo.semillas)
    print(f"    Mejor semilla: {res_modelo.mejor_semilla} · inercia {res_modelo.kmeans.inertia_ / 1e6:.4f} millones"
          f" · {estables} de {len(res_modelo.semillas)} semillas llegan a los mismos grupos")

    paso("3/4 Nombrando perfiles y calculando cruces…")
    tablas = resultados.calcular(prep, res_modelo)
    tablas["metricas_modelo"]["datos"] = ruta.name
    tablas["metricas_modelo"]["datos_falsos"] = falso
    perfiles = tablas["perfiles"].set_index("perfil")["pct"]
    for p in PERFILES:
        distinto = abs(perfiles[p] - ESPERADO[p]) > 0.2
        aviso = f"   <- distinto de las notebooks ({ESPERADO[p]})" if distinto and not falso else ""
        print(f"    {p:<28} {perfiles[p]:5.1f}%{aviso}")

    paso("4/4 Guardando artefactos…")
    for ruta in resultados.guardar(tablas, res_modelo):
        print(f"    {ruta.relative_to(config.RAIZ)}")

    print(f"\nListo en {time.time() - inicio:.0f} segundos. Ahora: streamlit run app/Inicio.py")


if __name__ == "__main__":
    main()
