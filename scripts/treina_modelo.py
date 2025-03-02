import pandas as pd
from sentence_transformers import SentenceTransformer
import joblib
import os
import numpy as np

DIR_PROCESSED = "./processed"
os.makedirs(DIR_PROCESSED, exist_ok=True)

df_itens = pd.read_csv(f"{DIR_PROCESSED}/itens_processados.csv")

try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    raise RuntimeError(f"Erro ao carregar modelo de embeddings: {str(e)}")

df_itens["category"] = df_itens["category"].fillna("unknown")
df_itens["title"] = df_itens["title"].fillna("")
df_itens["body"] = df_itens["body"].fillna("")

df_itens["full_text"] = df_itens["title"] + " " + df_itens["body"].apply(lambda x: " ".join(x.split()[:50]))

print("Gerando embeddings das notícias...")
df_itens["embeddings"] = df_itens["full_text"].apply(lambda x: model.encode(str(x)) if isinstance(x, str) else np.zeros(384))
df_itens["embeddings"] = df_itens["embeddings"].apply(lambda x: x.tolist())
df_itens = df_itens.dropna(subset=["embeddings"])

joblib.dump(df_itens[["page", "title", "category", "embeddings"]], f"{DIR_PROCESSED}/embeddings_noticias.pkl")

print(f"Embeddings treinados e salvos em {DIR_PROCESSED}")
