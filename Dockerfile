# 1. Imagem base
FROM python:3.14-slim

# 2. Variáveis de ambiente básicas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Instalar dependências do sistema (pq vamos usar poetry)
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*

# 4. Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python - --version 2.2.1
ENV PATH="/root/.local/bin:$PATH"

# 5. Criar pasta do app
WORKDIR /app

# 6. Copiar pyproject e lock primeiro (cache)
COPY pyproject.toml poetry.lock* /app/

# 7. Instalar deps (sem criar virtualenv e IGNORANDO o projeto raiz)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root
#                                              ^^^^^^^^^^^ <-- CORREÇÃO AQUI

# 8. Copiar o resto do código
COPY . /app

# 9. Expor porta
EXPOSE 8000

# 10. Comando de start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]