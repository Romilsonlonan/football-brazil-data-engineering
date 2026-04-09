"""Pipeline Gold - Calendário de Jogos (Prontos para consumo)"""

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

from src.configs import settings

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TIME_NAME_MAP = {
    "Athletico-PR": "Athletico Paranaense",
    "Atlético-MG": "Atlético Mineiro",
    "Bahia": "Bahia",
    "Botafogo": "Botafogo",
    "Chapecoense": "Chapecoense",
    "Corinthians": "Corinthians",
    "Coritiba": "Coritiba",
    "Cruzeiro": "Cruzeiro",
    "Flamengo": "Flamengo",
    "Fluminense": "Fluminense",
    "Grêmio": "Grêmio",
    "Internacional": "Internacional",
    "Mirassol": "Mirassol",
    "Palmeiras": "Palmeiras",
    "Red Bull Bragantino": "Bragantino",
    "Remo": "Remo",
    "Santos": "Santos",
    "São Paulo": "São Paulo",
    "Vasco da Gama": "Vasco",
    "Vitória": "Vitória",
}


class GoldCalendario:
    """Pipeline Gold para dados de calendário."""

    def __init__(self):
        self.table_name = "gold_calendario"
        self.schema_name = "public"

    def run(self, month: int = 4, year: int = 2026) -> dict:
        """Executa o pipeline Gold completo."""
        logger.info("=" * 60)
        logger.info("🔄 PIPELINE GOLD - CALENDÁRIO")
        logger.info("Carregando dados para PostgreSQL/Superset")
        logger.info("=" * 60)

        df = self._ler_dados_silver(month, year)
        gold_path = self._salvar_parquet(df, month, year)
        self._carregar_postgresql(df)

        logger.info("=" * 60)
        logger.info("✅ PIPELINE GOLD - CALENDÁRIO CONCLUÍDO!")
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

    def _ler_dados_silver(self, month: int, year: int) -> pd.DataFrame:
        """Lê dados da camada Silver."""
        silver_path = settings.silver_path / f"calendario_{year}_{month:02d}.parquet"

        if not silver_path.exists():
            raise FileNotFoundError(f"Arquivo Silver não encontrado: {silver_path}")

        logger.info(f"Lendo dados de: {silver_path}")
        df = pd.read_parquet(silver_path)

        if df.empty:
            raise ValueError("DataFrame está vazio.")

        df = df.copy()

        if "time" in df.columns:
            df["time_normalizado"] = df["time"].map(TIME_NAME_MAP).fillna(df["time"])

        cols_ordem = [
            "time",
            "time_normalizado",
            "DATA",
            "JOGO",
            "HORA",
            "status",
            "mes",
            "ano",
        ]
        cols_existentes = [c for c in cols_ordem if c in df.columns]
        df = df[cols_existentes]

        logger.info(f"Arquivo lido: {len(df)} registros")

        return df

    def _salvar_parquet(self, df: pd.DataFrame, month: int, year: int) -> Path:
        """Salva arquivo Parquet na camada Gold."""
        gold_path = settings.gold_path
        gold_path.mkdir(parents=True, exist_ok=True)

        gold_file = gold_path / f"calendario_{year}_{month:02d}.parquet"
        df.to_parquet(gold_file, index=False)

        logger.info(f"Arquivo Parquet salvo: {gold_file}")

        if settings.minio_enabled:
            from src.utils.minio_client import save_to_minio

            minio_path = save_to_minio(
                df, "gold", f"calendario_{year}_{month:02d}.parquet"
            )
            if minio_path:
                logger.info(f"☁️  Arquivo Parquet salvo no MinIO: {minio_path}")
            else:
                logger.warning("⚠️  Falha ao salvar no MinIO")

        return gold_file

    def _carregar_postgresql(self, df: pd.DataFrame) -> None:
        """Carrega dados para PostgreSQL."""
        from src.configs import settings

        if not settings.postgres_user:
            raise ValueError("postgres_user é obrigatório.")
        if not settings.postgres_password:
            raise ValueError("postgres_password é obrigatório.")
        if not settings.postgres_host:
            raise ValueError("postgres_host é obrigatório.")
        if not settings.postgres_db:
            raise ValueError("postgres_db é obrigatório.")
        if settings.postgres_port == 0:
            raise ValueError("postgres_port é obrigatório.")

        engine = create_engine(settings.postgres_url)

        with engine.connect() as conn:
            conn.execute(
                text(f'DROP TABLE IF EXISTS "{self.schema_name}"."{self.table_name}"')
            )
            conn.commit()

        df.to_sql(
            self.table_name,
            engine,
            schema=self.schema_name,
            if_exists="replace",
            index=False,
        )

        logger.info(
            f"Dados carregados para PostgreSQL: {self.schema_name}.{self.table_name}"
        )


def run(month: int = 4, year: int = 2026) -> dict:
    """Função de entrada para executar o pipeline Gold."""
    pipeline = GoldCalendario()
    return pipeline.run(month, year)


if __name__ == "__main__":
    run(month=4, year=2026)
