import pandas as pd
import glob
import os

DIR_ITENS = "./data/itens"
DIR_TREINO = "./data/treino"
DIR_PROCESSED = "./processed"

os.makedirs(DIR_PROCESSED, exist_ok=True)

def extrair_categoria(url):
    categorias_possiveis = ["politica", "economia", "esporte", "ciencia", "mundo", "tecnologia", "entretenimento"]
    for categoria in categorias_possiveis:
        if f"/{categoria}/" in url:
            return categoria
    return "geral"

def carregar_itens():
    arquivos_itens = glob.glob(f"{DIR_ITENS}/*.csv")

    if not arquivos_itens:
        raise FileNotFoundError("Nenhum arquivo de itens encontrado!")

    df_itens = pd.concat([pd.read_csv(f, encoding="utf-8") for f in arquivos_itens], ignore_index=True)
    df_itens["category"] = df_itens["url"].astype(str).apply(extrair_categoria)
    df_itens.drop_duplicates(subset=["page"], inplace=True)

    return df_itens

def carregar_treino():
    arquivos_treino = glob.glob(f"{DIR_TREINO}/*.csv")

    if not arquivos_treino:
        raise FileNotFoundError("Nenhum arquivo de treino encontrado!")

    df_treino = pd.concat([pd.read_csv(f, encoding="utf-8") for f in arquivos_treino], ignore_index=True)
    return df_treino

if __name__ == "__main__":
    df_itens = carregar_itens()
    df_treino = carregar_treino()
    
    df_itens.to_csv(f"{DIR_PROCESSED}/itens_processados.csv", index=False)
    df_treino.to_csv(f"{DIR_PROCESSED}/treino_processado.csv", index=False)

    print(f"Dados processados e salvos em {DIR_PROCESSED}/")
