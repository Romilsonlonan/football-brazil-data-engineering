"""Pipeline Gold - Carga para PostgreSQL/Superset.
========================================================

Este pipeline é responsável por:
- Ler os dados da camada Silver (dados tratados)
- Carregar os dados no PostgreSQL (banco do Superset)
- Criar a tabela ready-to-use para visualização

Fluxo:
    Bronze (Raw) → Silver (Tratado) → Gold (PostgreSQL/Superset)

Tags: gold, carga, postgresql, superset, classificacao
"""

import logging

import pandas as pd
from sqlalchemy import create_engine, text

from src.configs import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run():
    """Executa o pipeline Gold de carga de classificação."""
    logger.info("=" * 60)
    logger.info("🔄 PIPELINE GOLD - CARGA CLASSIFICAÇÃO")
    logger.info("Carregando dados para PostgreSQL/Superset")
    logger.info("=" * 60)

    # Caminho do arquivo Silver
    silver_path = settings.silver_path / "classificacao-limpa.parquet"

    if not silver_path.exists():
        raise FileNotFoundError(f"Arquivo Silver não encontrado: {silver_path}")

    logger.info(f"Lendo dados de: {silver_path}")

    # Ler arquivo Parquet
    df = pd.read_parquet(silver_path)
    # Validar que o DataFrame não está vazio
    if df.empty:
        raise ValueError(
            "DataFrame está vazio. Não há dados para carregar no PostgreSQL."
        )

    logger.info(f"Arquivo lido: {len(df)} registros, {len(df.columns)} colunas")
    logger.info(f"Colunas: {df.columns.tolist()}")

    # ============================================
    # ETAPA 1: Salvar arquivo Parquet na Gold
    # ============================================
    logger.info("")
    logger.info("💾 ETAPA 1: Salvando arquivo Parquet na Gold...")

    gold_path = settings.gold_path / "classificacao.parquet"
    gold_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(gold_path, index=False)
    logger.info(f"✅ Arquivo Parquet salvo em: {gold_path}")

    # ============================================
    # ETAPA 2: Carregar para PostgreSQL
    # ============================================
    logger.info("")
    logger.info("💽 ETAPA 2: Carregando dados para PostgreSQL...")

    # Conectar ao PostgreSQL
    postgres_user = settings.postgres_user
    postgres_password = settings.postgres_password
    postgres_host = settings.postgres_host
    postgres_port = str(settings.postgres_port)  # Converter para string
    postgres_db = settings.postgres_db

    # Validate required credentials
    if not postgres_user:
        raise ValueError(
            "postgres_user setting is required. Configure via POSTGRES_USER env variable."
        )
    if not postgres_password:
        raise ValueError(
            "postgres_password setting is required. Configure via POSTGRES_PASSWORD env variable."
        )
    if not postgres_host:
        raise ValueError(
            "postgres_host setting is required. Configure via POSTGRES_HOST env variable."
        )
    if not postgres_db:
        raise ValueError(
            "postgres_db setting is required. Configure via POSTGRES_DB env variable."
        )
    if settings.postgres_port == 0:
        raise ValueError(
            "postgres_port setting is required. Configure via POSTGRES_PORT env variable."
        )

    conn_string = f"postgresql+psycopg2://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    logger.info(
        f"Conectando ao PostgreSQL em {postgres_host}:{postgres_port}/{postgres_db}"
    )

    engine = create_engine(conn_string)

    # Testar conexão
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        logger.info(f"Conexão estabelecida: {version[:50]}...")

    # Nome da tabela no PostgreSQL (hardcoded para evitar SQL injection via input externo)
    table_name = "gold_classificacao"
    schema_name = "public"

    # Inserir dados
    logger.info(f"Inserindo dados na tabela: {schema_name}.{table_name}")

    # Usar SQLAlchemy para inserção (mais seguro)
    with engine.begin() as conn:
        # Verificar se tabela existe
        result = conn.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = :schema_name
                AND table_name = :table_name
            )
        """),
            {"schema_name": schema_name, "table_name": table_name},
        )
        table_exists = result.fetchone()[0]

        if table_exists:
            logger.info(
                f"Tabela '{schema_name}.{table_name}' existe. Verificando dados existentes..."
            )
            # Usar sqlalchemy.text com formato correto para schema.table
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
            )
            existing_count = result.fetchone()[0]
            logger.info(f"Registros existentes: {existing_count}")

    # Inserir dados (replace - apaga e recria)
    df.to_sql(table_name, engine, schema=schema_name, if_exists="replace", index=False)

    logger.info(
        f"✅ Sucesso! {len(df)} registros inseridos na tabela '{schema_name}.{table_name}'"
    )

    logger.info("=" * 60)
    logger.info("✅ PIPELINE GOLD - CARGA CONCLUÍDA!")
    logger.info(f"   Registros: {len(df)}")
    logger.info("   Tabela: public.gold_classificacao")
    logger.info("=" * 60)
    logger.info("")
    logger.info("💡 DICA: Para atualizar o Superset:")
    logger.info("   1. Vá no gráfico do Superset")
    logger.info("   2. Clique nos três pontinhos (menu)")
    logger.info("   3. Selecione 'Force refresh'")

    return {"rows_inserted": len(df), "table_name": table_name, "status": "SUCCESS"}


if __name__ == "__main__":
    run()
