"""Pipeline Gold - Carga de Elenco Jogadores de Campo para PostgreSQL/Superset.
============================================================================

Este pipeline e responsavel por:
- Ler os dados da camada Silver (dados tratados)
- Carregar os dados no PostgreSQL (banco do Superset)
- Criar a tabela ready-to-use para visualizacao

Fluxo:
    Bronze (Raw) -> Silver (Tratado) -> Gold (PostgreSQL/Superset)

Tags: gold, carga, postgresql, superset, jogadores_campo, elenco
"""

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from src.configs import settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GoldCargaElencoJogadoresCampo:
    """Pipeline Gold para carga de dados de jogadores de campo para PostgreSQL/Superset."""

    def __init__(self):
        """Inicializa o pipeline Gold."""
        self.table_name = "gold_elenco_jogadores_campo"
        self.schema_name = "public"

    def run(self) -> dict:
        """Executa o pipeline Gold completo."""
        logger.info("=" * 60)
        logger.info("🔄 PIPELINE GOLD - CARGA ELENCO JOGADORES DE CAMPO")
        logger.info("Carregando dados para PostgreSQL/Superset")
        logger.info("=" * 60)

        # ============================================
        # ETAPA 1: Ler dados da Silver
        # ============================================
        df = self._ler_dados_silver()

        # ============================================
        # ETAPA 2: Salvar arquivo Parquet na Gold
        # ============================================
        gold_path = self._salvar_parquet(df)

        # ============================================
        # ETAPA 3: Carregar para PostgreSQL
        # ============================================
        self._carregar_postgresql(df)

        logger.info("=" * 60)
        logger.info("✅ PIPELINE GOLD - CARGA CONCLUÍDA!")
        logger.info(f"   Registros: {len(df)}")
        logger.info(f"   Tabela: {self.schema_name}.{self.table_name}")
        logger.info(f"   Arquivo: {gold_path}")
        logger.info("=" * 60)

        return {
            "status": "success",
            "records": len(df),
            "table": f"{self.schema_name}.{self.table_name}",
            "gold_path": str(gold_path),
        }

    def _ler_dados_silver(self) -> pd.DataFrame:
        """Lee os dados da camada Silver."""
        silver_path = settings.silver_path / "elenco_jogadores_campo_tratados.parquet"

        if not silver_path.exists():
            raise FileNotFoundError(
                f"Arquivo Silver nao encontrado: {silver_path}"
            )

        logger.info(f"Lendo dados de: {silver_path}")

        df = pd.read_parquet(silver_path)

        if df.empty:
            raise ValueError(
                "DataFrame esta vazio. Nao ha dados para carregar no PostgreSQL."
            )

        logger.info(f"Arquivo lido: {len(df)} registros, {len(df.columns)} colunas")
        logger.info(f"Colunas: {df.columns.tolist()}")

        return df

    def _salvar_parquet(self, df: pd.DataFrame) -> Path:
        """Salva o arquivo Parquet na camada Gold."""
        logger.info("")
        logger.info("💾 ETAPA 1: Salvando arquivo Parquet na Gold...")

        gold_path = settings.gold_path / "elenco_jogadores_campo.parquet"
        gold_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_parquet(gold_path, index=False)
        logger.info(f"✅ Arquivo Parquet salvo em: {gold_path}")

        return gold_path

    def _carregar_postgresql(self, df: pd.DataFrame) -> None:
        """Carrega os dados para PostgreSQL."""
        logger.info("")
        logger.info("💽 ETAPA 2: Carregando dados para PostgreSQL...")

        # Validar credenciais
        postgres_user = settings.postgres_user
        postgres_password = settings.postgres_password
        postgres_host = settings.postgres_host
        postgres_port = str(settings.postgres_port)
        postgres_db = settings.postgres_db

        self._validar_credenciais(
            postgres_user,
            postgres_password,
            postgres_host,
            postgres_port,
            postgres_db,
        )

        # Criar conexao
        conn_string = (
            f"postgresql+psycopg2://{postgres_user}:{postgres_password}"
            f"@{postgres_host}:{postgres_port}/{postgres_db}"
        )

        logger.info(
            f"Conectando ao PostgreSQL em {postgres_host}:{postgres_port}/{postgres_db}"
        )

        engine = create_engine(conn_string)

        # Testar conexao
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Conexao estabelecida: {version[:50]}...")

        # Inserir dados
        logger.info(f"Inserindo dados na tabela: {self.schema_name}.{self.table_name}")

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
                {"schema_name": self.schema_name, "table_name": self.table_name},
            )
            table_exists = result.fetchone()[0]

            if table_exists:
                logger.info(
                    f"Tabela '{self.schema_name}.{self.table_name}' existe. "
                    f"Verificando dados existentes..."
                )
                result = conn.execute(
                    text(
                        f"SELECT COUNT(*) FROM {self.schema_name}.{self.table_name}"
                    )
                )
                existing_count = result.fetchone()[0]
                logger.info(f"Registros existentes: {existing_count}")

        # Inserir dados (replace - apaga e recria)
        df.to_sql(
            self.table_name,
            engine,
            schema=self.schema_name,
            if_exists="replace",
            index=False,
        )

        logger.info(
            f"✅ Sucesso! {len(df)} registros inseridos na tabela "
            f"'{self.schema_name}.{self.table_name}'"
        )

    def _validar_credenciais(
        self,
        postgres_user: str,
        postgres_password: str,
        postgres_host: str,
        postgres_port: str,
        postgres_db: str,
    ) -> None:
        """Valida as credenciais do PostgreSQL."""
        if not postgres_user:
            raise ValueError(
                "postgres_user setting is required. "
                "Configure via POSTGRES_USER env variable."
            )
        if not postgres_password:
            raise ValueError(
                "postgres_password setting is required. "
                "Configure via POSTGRES_PASSWORD env variable."
            )
        if not postgres_host:
            raise ValueError(
                "postgres_host setting is required. "
                "Configure via POSTGRES_HOST env variable."
            )
        if not postgres_db:
            raise ValueError(
                "postgres_db setting is required. "
                "Configure via POSTGRES_DB env variable."
            )
        if settings.postgres_port == 0:
            raise ValueError(
                "postgres_port setting is required. "
                "Configure via POSTGRES_PORT env variable."
            )


def run() -> dict:
    """Funcao de entrada para executar o pipeline Gold."""
    pipeline = GoldCargaElencoJogadoresCampo()
    return pipeline.run()


if __name__ == "__main__":
    run()
