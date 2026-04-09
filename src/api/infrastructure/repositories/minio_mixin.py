"""Mixin para repositórios que leem dados do MinIO."""

import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


class MinIODataFrameMixin:
    """Mixin para carregar DataFrames do MinIO."""

    _minio_client = None
    _local_fallback_enabled = True

    @classmethod
    def _get_minio_client(cls):
        """Retorna cliente MinIO (singleton)."""
        if cls._minio_client is None:
            try:
                from src.utils.minio_client import MinIOClient

                cls._minio_client = MinIOClient()
            except Exception as e:
                logger.warning(f"MinIO não disponível: {e}")
                cls._minio_client = None
        return cls._minio_client

    @classmethod
    def _load_from_minio(cls, folder: str, filename: str) -> pd.DataFrame:
        """Carrega DataFrame do MinIO.

        Args:
            folder: Pasta no bucket (bronze/silver/gold)
            filename: Nome do arquivo

        Returns:
            DataFrame do MinIO ou do disco local se não encontrar
        """
        client = cls._get_minio_client()

        if client is not None:
            try:
                df = client.read_parquet(folder, filename)
                if df is not None and not df.empty:
                    logger.info(f"Dados carregados do MinIO: {folder}/{filename}")
                    return df
                else:
                    logger.warning(f"Arquivo vazio no MinIO: {folder}/{filename}")
            except Exception as e:
                logger.warning(f"Erro ao ler do MinIO, tentando local: {e}")

        # Fallback para disco local
        if cls._local_fallback_enabled:
            return cls._load_from_local(folder, filename)

        return cls._empty_dataframe()

    @classmethod
    def _load_from_local(cls, folder: str, filename: str) -> pd.DataFrame:
        """Carrega DataFrame do disco local."""
        data_path = os.environ.get("DATA_PATH", "/app/data")
        local_path = Path(data_path) / folder / filename

        logger.info(f"Tentando ler do disco local: {local_path}")

        if local_path.exists():
            try:
                df = pd.read_parquet(local_path)
                logger.info(
                    f"Dados carregados do local: {local_path} ({len(df)} linhas)"
                )
                return df
            except Exception as e:
                logger.error(f"Erro ao ler arquivo local: {e}")

        logger.warning(f"Arquivo não encontrado localmente: {local_path}")
        return cls._empty_dataframe()

    @staticmethod
    def _empty_dataframe() -> pd.DataFrame:
        """Retorna DataFrame vazio com colunas padrão."""
        return pd.DataFrame(
            columns=[
                "posicao",
                "time",
                "jogos",
                "vitorias",
                "empates",
                "derrotas",
                "gols_pro",
                "gols_contra",
                "saldo_gols",
                "pontos",
            ]
        )
