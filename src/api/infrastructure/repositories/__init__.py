"""Repositórios da infraestrutura."""

from .parquet_classificacao_base_repository import ParquetClassificacaoBaseRepository
from .parquet_classificacao_vagas_repository import ParquetClassificacaoVagasRepository
from .parquet_repository import ParquetClassificacaoRepository

__all__ = [
    "ParquetClassificacaoRepository",
    "ParquetClassificacaoBaseRepository",
    "ParquetClassificacaoVagasRepository",
]
