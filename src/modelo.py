"""Gestión de modelos: elección de k, k-means y controles de estabilidad."""

from dataclasses import dataclass, field

import numpy as np
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

from src import config


@dataclass
class ResultadoModelo:
    kmeans: KMeans
    mejor_semilla: int
    semillas: list = field(default_factory=list)      # [{semilla, inercia, ari}]
    codo: dict = field(default_factory=dict)          # k -> inercia
    silueta: dict = field(default_factory=dict)       # k -> silueta
    dendrograma: dict = field(default_factory=dict)   # icoord, dcoord, corte, ari


def elegir_k(X: np.ndarray, pesos: np.ndarray, rng: np.random.Generator) -> tuple[dict, dict, dict]:
    """Inercias del codo y silueta (sobre una muestra) para cada k."""
    muestra = rng.choice(len(X), size=config.MUESTRA_SILUETA, replace=False)
    codo, silueta, etiquetas_por_k = {}, {}, {}
    for k in config.K_CODO:
        modelo = KMeans(n_clusters=k, n_init=config.N_INIT_CODO, random_state=config.SEMILLA)
        modelo.fit(X, sample_weight=pesos)
        codo[k] = float(modelo.inertia_)
        etiquetas_por_k[k] = modelo.labels_
        if k >= 2:
            silueta[k] = float(silhouette_score(X[muestra], modelo.labels_[muestra]))
    return codo, silueta, etiquetas_por_k


def entrenar_kmeans(X: np.ndarray, pesos: np.ndarray) -> tuple[KMeans, int, list]:
    """Entrena con varias semillas y se queda con la de menor inercia.

    k-means puede quedar en un mínimo local; probar varias semillas y comparar
    las soluciones (ARI) muestra si el resultado es estable.
    """
    corridas = {}
    for semilla in config.SEMILLAS:
        modelo = KMeans(n_clusters=config.K, n_init=config.N_INIT, random_state=semilla)
        corridas[semilla] = modelo.fit(X, sample_weight=pesos)
    mejor = min(corridas, key=lambda s: corridas[s].inertia_)
    etiquetas = corridas[mejor].labels_
    semillas = [
        {"semilla": s, "inercia": float(m.inertia_), "ari": float(adjusted_rand_score(etiquetas, m.labels_))}
        for s, m in corridas.items()
    ]
    return corridas[mejor], mejor, semillas


def dendrograma_de_control(X: np.ndarray, etiquetas_kmeans: np.ndarray, rng: np.random.Generator) -> dict:
    """Ward sobre una muestra: sirve para ver si cortar en k grupos es razonable."""
    muestra = rng.choice(len(X), size=config.MUESTRA_DENDROGRAMA, replace=False)
    enlaces = linkage(X[muestra], method="ward")
    alturas = enlaces[:, 2]
    corte = float((alturas[-config.K] + alturas[-config.K + 1]) / 2)
    dibujo = dendrogram(enlaces, truncate_mode="lastp", p=config.HOJAS_DENDROGRAMA, no_plot=True)
    grupos = fcluster(enlaces, t=config.K, criterion="maxclust")
    return {
        "icoord": dibujo["icoord"],
        "dcoord": dibujo["dcoord"],
        "corte": corte,
        "muestra": config.MUESTRA_DENDROGRAMA,
        "ari_con_kmeans": float(adjusted_rand_score(etiquetas_kmeans[muestra], grupos)),
    }


def entrenar(X: np.ndarray, pesos: np.ndarray) -> ResultadoModelo:
    rng = np.random.default_rng(config.SEMILLA)
    codo, silueta, _ = elegir_k(X, pesos, rng)
    kmeans, mejor, semillas = entrenar_kmeans(X, pesos)
    dendro = dendrograma_de_control(X, kmeans.labels_, rng)
    return ResultadoModelo(kmeans=kmeans, mejor_semilla=mejor, semillas=semillas,
                           codo=codo, silueta=silueta, dendrograma=dendro)
