import pandas as pd
import joblib
import numpy as np
from sklearn.cluster import KMeans
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

DIR_PROCESSED = "./processed"
os.makedirs(DIR_PROCESSED, exist_ok=True)

print("Carregando embeddings...")
embeddings_data = joblib.load(f"{DIR_PROCESSED}/embeddings_noticias.pkl")

news_ids = embeddings_data["page"].values
embeddings_matrix = np.vstack(embeddings_data["embeddings"].values)

def encontrar_numero_ideal_clusters(embeddings_matrix, max_k=15):
    distortions = []
    K = range(2, max_k)
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(embeddings_matrix)
        distortions.append(kmeans.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(K, distortions, 'bx-')
    plt.xlabel('Número de Clusters (k)')
    plt.ylabel('Distortion (Inertia)')
    plt.title('Método do Cotovelo para Encontrar k')
    plt.savefig(f"{DIR_PROCESSED}/elbow_method.png")
    plt.show()

    return distortions

print("Encontrando número ideal de clusters...")
distortions = encontrar_numero_ideal_clusters(embeddings_matrix)

NUM_CLUSTERS = 10  # Ajustável conforme necessário

print(f"Aplicando K-Means com {NUM_CLUSTERS} clusters...")
kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=42, n_init=10)
clusters = kmeans.fit_predict(embeddings_matrix)

embeddings_data["cluster"] = clusters

joblib.dump(embeddings_data, f"{DIR_PROCESSED}/embeddings_noticias_clusterizados.pkl")
print(f"Clusterização concluída! Dados salvos em {DIR_PROCESSED}/embeddings_noticias_clusterizados.pkl")
