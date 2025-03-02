# Globo - Sistema de Recomendação para G1

## Objetivo
Desenvolver um sistema de recomendação de notícias para o portal G1 predizendo qual será a próxima notícia que o usuário vai ler.  

---

## Estratégia de Recomendacão Empregada

Utilizamos um **modelo híbrido** que combina:

1. **Content-Based Filtering** com embeddings de notícias.
2. **Clusterização K-Means** para agrupar notícias similares.
3. **Modelo de Similaridade do Tipo Item-Item** usando similaridade de cosseno.
4. **Recomendação Híbrida para Cold-Start de Usuários** (notícias populares + recentes + exploratórias).

### Porque foi empregado um modelo híbrido? 

Vamos dar uma olhada nos dois cenários princinpais que mapeamos, seus desafios e possíveis soluções: 

**Cenário 1: Cold-start para Itens (Notícias Novas)**

Se uma notícia nova for adicionada ao sistema sem histórico de leitura dos usuários, ela ainda pode ser recomendada com base na similaridade semântica do conteúdo, mas essa abordagem trás os seguintes problemas: 

- Uma notícia nova pode não ser recomendada inicialmente pois não há interação de usuários para reforçar sua relevância.
- Se a categoria da notícia estiver errada ou o título for muito genérico o embedding pode ser menos representativo.

Entre as possíveis soluções para este cenário, temos: 

- Explorar a popularidade inicial: notícias novas podem ser recomendadas mais frequentemente nos primeiros minutos/horas com base na categoria ou trending topics.
- Aproveitar metadados adicionais: usar dados como autor, palavras-chave ou até sumarizações para enriquecer os embeddings.
- Incorporar um modelo híbrido: misturar similaridade de conteúdo com um fator de exploração baseada em novidades.

**Cenário 2: Cold-start para Usuários Novos**

Atualmente, um usuário precisa ter um histórico de leitura para receber recomendações precisas. Se um usuário não tiver interações anteriores, ele não poderá receber recomendações personalizadas:

- Sem histórico, não há como prever a próxima leitura com base na similaridade com conteúdos anteriores.

Possíveis soluções:

- Popularidade inicial: para novos usuários, recomendar notícias mais populares do momento até que eles interajam com alguma.
- Questionário de preferências: pedir ao usuário que selecione categorias de interesse no primeiro acesso.
- Basear-se em perfis similares: se um usuário novo se comporta como outros usuários (ex.: leitura inicial de política), ele pode receber recomendações com base nesses perfis.

Foi por isso que criamos uma estratégia híbrida: para combinar múltiplas abordagens de recomendação, garantindo que novos usuários recebam sugestões relevantes sem depender de um único critério. 

---

## Modelo de Embeddings
- Utilizamos o **all-MiniLM-L6-v2**, um modelo de embeddings da **SentenceTransformers** que equilibra **precisão** e **eficiência computacional**.
- Cada notícia é transformada em um vetor de 384 dimensões, permitindo cálculos rápidos de similaridade.

**Cálculo da Similaridade**:
$$
sim(A, B) = \frac{A \cdot B}{||A|| \times ||B||}
$$

Ainda com relação ao modelo escolhido, ele apresenta um bom equilibrio entre precisão e eficiência computacional. 

O **all-MiniLM-L6-v2** é uma versão otimizada do BERT, reduzindo a complexidade e mantendo boa qualidade dos embeddings. Ele possui: 

- Latencia Baixa: 6 camadas de autoatenção (mais rápido que o BERT-base)
- Dimensão Reduzida (384 dimensões): menor custo computacional
- Boa performance sem necessidade de treinamento supervisionado

Existem modelos maiores como o BERT-base e o RoBERTa, que oferecem um leve ganho na similaridade semântica, mas com um custo maior de tempo de inferência. Como tomamos a decisão de manter um tempo de resposta baixo na API, escolhemos o MiniLM. 

Se o tempo de resposta e o custo não fossem um problema, teríamos escolhido o ColBERT + Multi-Armed Bandids (RL). 

O ColBERT melhora drasticamente a busca de similaridade com um modelo mais refinado do que MiniLM. O Multi-Armed Bandits permitiria um sistema de autoaprendizagem que testa recomendações e se ajusta dinamicamente. E além disso ainda poderíamos combinar Clusterização + RL + embeddings de um modelo potente, resultando em um sistema de recomendação mais robusto.

---

## Clusterização de Notícias
- Aplicamos **K-Means** nos embeddings para agrupar notícias semelhantes.
- O **número de clusters** foi determinado com o **método do cotovelo**.
- Cada notícia pertence a um cluster, permitindo recomendações **diversificadas** dentro de grupos similares.

---

## Modelo Híbrido para Cold-Start
Quando um usuário não tem histórico de leitura, usamos a seguinte estratégia:

1. **Notícias Populares**: Top-N notícias com mais acessos.
2. **Notícias Recentes**: Mais novas no período de 3 dias.
3. **Notícias Explorátorias**: Sorteio de clusters para diversidade.

O **score final** de cada notícia é definido por:
$$
Score = \alpha \times Popularidade + \beta \times Recência + \gamma \times Diversidade
$$

Onde:
$$
\alpha, \beta, \gamma \text{ são hiperparâmetros ajustáveis.}
$$


---

## Documentação dos Scripts

O pipeline do projeto foi dividido em **quatro etapas** principais: **processamento**, **treinamento dos embeddings**, **clusterização** e **implementação da API**.

### 1. Processamento dos Dados

**Arquivo:** `scripts/processar_dados.py`  
**Objetivo:** Limpar e organizar os dados brutos das notícias.  

**Principais etapas:**
- Remoção de dados inválidos e tratamento de nulos.
- Extração de informações estruturadas (ex: título, categoria).
- Geração do dataset `itens_processados.csv` utilizado nos modelos.

**Execução:**
```bash
python scripts/processar_dados.py
```

---

### 2. Treinamento dos Embeddings

**Arquivo:** `scripts/treinar_embeddings.py`  
**Objetivo:** Gerar embeddings das notícias utilizando o modelo **all-MiniLM-L6-v2**.

**Principais etapas:**
- Carregamento do dataset `itens_processados.csv`.
- Aplicação do modelo para transformar as notícias em vetores.
- Salvamento dos embeddings em `embeddings_noticias.pkl`.

**Execução:**
```bash
python scripts/treinar_embeddings.py
```

---

### 3. Clusterização das Notícias

**Arquivo:** `scripts/clusterizar_noticias.py`  
**Objetivo:** Aplicar **K-Means** nos embeddings para agrupar notícias em clusters.

**Principais etapas:**
- Carregamento dos embeddings `embeddings_noticias.pkl`.
- Aplicação do algoritmo **K-Means** e determinação do melhor número de clusters usando o **método do cotovelo**.
- Salvamento do modelo de clusters em `embeddings_noticias_clusterizados.pkl`.

**Execução:**
```bash
python scripts/clusterizar_noticias.py
```

---

### 4. Testes da API

**Arquivo:** `tests/test_api.py`  
**Objetivo:** Validar o funcionamento dos endpoints da API.

**Principais testes implementados:**
- Verificação da resposta do endpoint `/recomendacao/similar/{noticia_id}`.
- Testes do endpoint `/recomendacao/coldstart` para novos usuários.
- Testes do endpoint `/recomendacao/novidades` para avaliar notícias recentes.

**Execução dos testes:**
```bash
python tests/test_api.py
```

---

## API de Recomendacão (FastAPI + Gunicorn)
A API foi construída usando **FastAPI** e empacotada com **Docker** para facilitação do deploy.

### Endpoints
- **GET /recomendacao/similar/{noticia_id}** → Retorna notícias similares.
- **GET /recomendacao/coldstart** → Recomendação para novos usuários.
- **GET /recomendacao/novidades** → Recomendação de notícias recentes.

**Execução no Servidor:**
```bash
uvicorn scripts.api_recomendacao:app --host 0.0.0.0 --port 8000
```

Para produção, utilizamos **Gunicorn**:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_recomendacao:app
```

---

## Deploy e Infraestrutura
O sistema foi empacotado em um container Docker:

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN mkdir -p /app/processed

COPY ./requirements.txt ./requirements.txt
COPY ./scripts/api_recomendacao.py ./api_recomendacao.py
COPY ./gunicorn_config.py ./gunicorn_config.py
COPY ./processed /app/processed/

RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir --timeout=120 --retries=10 -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn_config.py", "api_recomendacao:app"]
```

**Execução do Container:**
```bash
docker build -t recomendacao-globo .
docker run -p 8000:8000 recomendacao-globo
```

---

## Testes e Validação
- **Latência esperada**: Menos de **200ms** por requisição.
- **Validação manual**: Testes qualitativos foram feitos verificando se as recomendações retornadas fazem sentido com base no contexto e categoria das notícias.

---

## Conclusão
- Conseguimos criar um sistema de recomendação eficiente e escalável.
- Para o futuro poderia ser incluídas melhorias com aprendizado por reforço para otimizar as recomendações dinâmicas.
