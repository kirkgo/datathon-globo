import pandas as pd
import joblib
from fastapi import FastAPI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import random
from datetime import datetime, timezone

app = FastAPI()

DIR_PROCESSED = "./processed"

df_itens = pd.read_csv(f"{DIR_PROCESSED}/itens_processados.csv")
embeddings_data = joblib.load(f"{DIR_PROCESSED}/embeddings_noticias_clusterizados.pkl")

dict_embeddings = {row["page"]: np.array(row["embeddings"]) for _, row in embeddings_data.iterrows()}
dict_clusters = {row["page"]: row["cluster"] for _, row in embeddings_data.iterrows()}
dict_info = df_itens.set_index("page")[["title", "category"]].to_dict(orient="index")

@app.get("/")
def home():
    return {"mensagem": "API de Recomendação Ativa!"}

@app.get("/recomendacao/similar/{noticia_id}")
def recomendar_similares(noticia_id: str, top_n: int = 5, diversidade: float = 0.3):
    """
    Retorna notícias similares com um mix de diversidade.
    """
    if noticia_id not in dict_embeddings:
        return {"erro": "Notícia não encontrada"}

    noticia_alvo = dict_info.get(noticia_id, {})
    cluster_alvo = dict_clusters.get(noticia_id, -1)

    embedding_target = dict_embeddings[noticia_id].reshape(1, -1)

    all_embeddings = np.array(list(dict_embeddings.values()))
    similaridades = cosine_similarity(embedding_target, all_embeddings)[0]

    noticias_similares_idx = np.argsort(similaridades)[::-1][1:]  # Exclui a própria notícia
    noticias_similares_ids = list(dict_embeddings.keys())

    noticias_cluster = [id_ for id_ in noticias_similares_ids if dict_clusters.get(id_) == cluster_alvo]

    num_diversas = int(top_n * diversidade)
    noticias_outros_clusters = [id_ for id_ in noticias_similares_ids if dict_clusters.get(id_) != cluster_alvo]
    random.shuffle(noticias_outros_clusters)

    recomendacoes = noticias_cluster[: top_n - num_diversas] + noticias_outros_clusters[:num_diversas]
    recomendacoes_formatadas = [
        {
            "id": id_,
            "titulo": dict_info.get(id_, {}).get("title", "Título Desconhecido"),
            "categoria": dict_info.get(id_, {}).get("category", "Desconhecido"),
            "cluster": dict_clusters.get(id_, -1),
        }
        for id_ in recomendacoes
    ]

    return {
        "noticia_id": noticia_id,
        "titulo": noticia_alvo.get("title", "Título Desconhecido"),
        "categoria": noticia_alvo.get("category", "Desconhecido"),
        "cluster": cluster_alvo,
        "recomendacoes": recomendacoes_formatadas
    }

@app.get("/recomendacao/coldstart")
def recomendar_cold_start(top_n: int = 5):
    """
    Recomenda notícias para usuários novos (sem histórico).
    """
    if "page" not in df_itens.columns:
        return {"erro": "A coluna 'page' não foi encontrada no dataset"}

    noticias_populares = df_itens.sample(n=min(top_n * 2, len(df_itens)), random_state=42)["page"].tolist()

    df_itens["issued"] = pd.to_datetime(df_itens["issued"], errors="coerce").fillna(datetime(2000, 1, 1, tzinfo=timezone.utc))
    noticias_recentes = df_itens.sort_values(by="issued", ascending=False).head(top_n * 2)["page"].tolist()

    clusters_disponiveis = df_itens["cluster"].unique() if "cluster" in df_itens.columns else []
    noticias_exploratorias = []
    for cluster in clusters_disponiveis:
        amostras = df_itens[df_itens["cluster"] == cluster].sample(n=1, random_state=42)["page"].tolist()
        noticias_exploratorias.extend(amostras)

    recomendacoes = list(set(noticias_populares[:top_n] + noticias_recentes[:top_n] + noticias_exploratorias[:top_n]))
    recomendacoes_formatadas = [
        {
            "id": id_,
            "titulo": dict_info.get(id_, {}).get("title", "Título Desconhecido"),
            "categoria": dict_info.get(id_, {}).get("category", "Desconhecido"),
            "cluster": dict_clusters.get(id_, -1),
        }
        for id_ in recomendacoes
    ]

    return {
        "mensagem": "Recomendações para novo usuário",
        "recomendacoes": recomendacoes_formatadas
    }

@app.get("/recomendacao/novidades")
def recomendar_novidades(top_n: int = 5):
    """
    Recomenda notícias novas para incentivar visibilidade no início.
    """
    dias_boost = 3
    hoje = datetime.now(timezone.utc)

    df_itens["issued"] = pd.to_datetime(df_itens["issued"], errors="coerce").fillna(datetime(2000, 1, 1, tzinfo=timezone.utc))

    noticias_novas = df_itens[df_itens["issued"] > (hoje - pd.Timedelta(days=dias_boost))]["page"].tolist()
    noticias_exploratorias = df_itens.sample(n=min(top_n, len(df_itens)), random_state=42)["page"].tolist()

    recomendacoes = list(set(noticias_novas[:top_n] + noticias_exploratorias[:top_n]))
    recomendacoes_formatadas = [
        {
            "id": id_,
            "titulo": dict_info.get(id_, {}).get("title", "Título Desconhecido"),
            "categoria": dict_info.get(id_, {}).get("category", "Desconhecido"),
            "cluster": dict_clusters.get(id_, -1),
        }
        for id_ in recomendacoes
    ]

    return {
        "mensagem": "Recomendações de notícias novas",
        "recomendacoes": recomendacoes_formatadas
    }
