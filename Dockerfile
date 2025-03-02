# 🔹 1. Usar uma imagem oficial do Python otimizada
FROM python:3.12-slim

# 🔹 2. Definir o diretório de trabalho dentro do container
WORKDIR /app

# 🔹 3. Criar diretório para arquivos processados
RUN mkdir -p /app/processed

# 🔹 4. Copiar os arquivos necessários
COPY ./requirements.txt ./requirements.txt
COPY ./scripts/api_recomendacao.py ./api_recomendacao.py
COPY ./gunicorn_config.py ./gunicorn_config.py
COPY ./processed /app/processed/

# 🔹 5. Instalar dependências do sistema (incluindo git para repositórios privados)
RUN apt-get update && apt-get install -y git

# 🔹 6. Instalar as dependências Python
RUN pip install --no-cache-dir --timeout=120 --retries=10 -r requirements.txt

# 🔹 7. Expor a porta do FastAPI
EXPOSE 8000

# 🔹 8. Comando para rodar a API em produção
CMD ["gunicorn", "-c", "gunicorn_config.py", "api_recomendacao:app"]
