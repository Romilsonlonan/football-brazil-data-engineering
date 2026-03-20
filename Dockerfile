# ============================================
# Dockerfile - Lakehouse Brasileiro
# ============================================
# Imagem base oficial Python
FROM python:3.12-slim

# Labels de metadados
LABEL maintainer="Romilson Luis"
LABEL description="Pipeline de dados do Campeonato Brasileiro"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONFAULTHANDLER=1

# Usuário não-root para segurança (criado dinamicamente)
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Diretório de trabalho
WORKDIR /app

# Copia primeiro o arquivo de dependências para cache
COPY --chown=appuser:appgroup pyproject.toml ./

# Instala dependências diretamente com pip
# Inclui todas as dependências do pyproject.toml
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages \
    fastapi \
    uvicorn[standard] \
    requests \
    pendulum \
    rich \
    pandas \
    python-dotenv \
    pydantic-settings \
    beautifulsoup4 \
    pyarrow \
    presidio-analyzer \
    presidio-anonymizer \
    spacy \
    piicatcher

# Copia código fonte
COPY --chown=appuser:appgroup src/ ./src/

# Copia dados silver (classificação)
COPY --chown=appuser:appgroup data/silver/ ./data/silver/

# Cria diretórios com permissões corretas
RUN mkdir -p /app/data/bronze /app/data/silver /app/data/gold /app/logs && \
    chown -R appuser:appgroup /app

# Copia script de entrypoint
COPY --chown=appuser:appgroup scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Troca para usuário não-root
USER appuser

# Define entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Exposta porta para API (FastAPI)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Comando padrão
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
