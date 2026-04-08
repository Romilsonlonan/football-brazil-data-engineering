"""Módulo para operações com MinIO/S3."""

import logging
from io import BytesIO
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class MinIOClient:
    """Cliente para salvar arquivos no MinIO (S3-compatible)."""

    def __init__(self, endpoint: str = "localhost:9000", bucket: str = "lakehouse"):
        try:
            from minio import Minio
            from src.configs import settings

            access_key = getattr(settings, "minio_access_key", "minioadmin")
            secret_key = getattr(settings, "minio_secret_key", "minioadmin")
            endpoint = getattr(settings, "minio_endpoint", "localhost:9000")

            self.client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=False,
            )
            self.bucket = bucket
            self._bucket_exists()
            logger.info(f"MinIO conectado: {endpoint}/{bucket}")

        except ImportError:
            logger.warning("Biblioteca 'minio' não instalada. Salvará apenas local.")
            self.client = None

    def _bucket_exists(self) -> None:
        """Cria bucket se não existir."""
        if self.client and not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)
            logger.info(f"Bucket criado: {self.bucket}")

    def save_parquet(
        self,
        df: pd.DataFrame,
        folder: str,
        filename: str,
    ) -> str | None:
        """Salva DataFrame como Parquet no MinIO.

        Args:
            df: DataFrame a ser salvo
            folder: Pasta no bucket (bronze/silver/gold)
            filename: Nome do arquivo

        Returns:
            Caminho no MinIO ou None se falhar
        """
        if not self.client:
            logger.warning("MinIO não disponível")
            return None

        try:
            object_name = f"{folder}/{filename}"
            buffer = BytesIO()
            df.to_parquet(buffer, index=False)
            buffer.seek(0)

            self.client.put_object(
                self.bucket,
                object_name,
                buffer,
                length=buffer.getbuffer().nbytes,
                content_type="application/octet-stream",
            )

            full_path = f"s3://{self.bucket}/{object_name}"
            logger.info(f"Salvo no MinIO: {full_path}")
            return full_path

        except Exception as e:
            logger.error(f"Erro ao salvar no MinIO: {e}")
            return None

    def read_parquet(self, folder: str, filename: str) -> pd.DataFrame | None:
        """Lê arquivo Parquet do MinIO."""
        if not self.client:
            return None

        try:
            object_name = f"{folder}/{filename}"
            response = self.client.get_object(self.bucket, object_name)
            df = pd.read_parquet(BytesIO(response.read()))
            logger.info(f"Lido do MinIO: {folder}/{filename}")
            return df

        except Exception as e:
            logger.error(f"Erro ao ler do MinIO: {e}")
            return None


def save_to_minio(df: pd.DataFrame, folder: str, filename: str) -> str | None:
    """Função utilitária para salvar no MinIO."""
    client = MinIOClient()
    return client.save_parquet(df, folder, filename)
