"""Repositório para ler dados do arquivo Parquet (classificação básica).

Este repositório lê dados do arquivo gold/classificacao.parquet do MinIO.
"""

import pandas as pd
from typing import List, Optional

from src.api.domain.entities.classificacao_base import ClassificacaoBase
from src.api.domain.entities.time import Time
from src.api.domain.repositories.interface import IClassificacaoRepository
from src.api.infrastructure.repositories.minio_mixin import MinIODataFrameMixin


class ParquetClassificacaoBaseRepository(IClassificacaoRepository, MinIODataFrameMixin):
    """Repositório que lê dados do arquivo Parquet Gold do MinIO."""

    def __init__(self, parquet_path: Optional[str] = None):
        """
        Inicializa o repositório.

        Args:
            parquet_path: Caminho para o arquivo parquet (descontinuado, usa MinIO).
        """
        self._folder = "gold"
        self._filename = "classificacao.parquet"
        self._df: Optional[pd.DataFrame] = None

    def _load_data(self) -> pd.DataFrame:
        """Carrega os dados do MinIO."""
        if self._df is None:
            self._df = self._load_from_minio(self._folder, self._filename)
        return self._df

    def _row_to_entity(
        self, row: pd.Series, temporada: Optional[str] = None
    ) -> ClassificacaoBase:
        """Converte uma linha do DataFrame para entidade ClassificacaoBase."""
        time_nome = row.get("time", "")
        time = Time(nome=str(time_nome))

        return ClassificacaoBase(
            posicao=int(row.get("posicao", 0)),
            time=time,
            jogos=int(row.get("jogos", 0)),
            vitorias=int(row.get("vitorias", 0)),
            empates=int(row.get("empates", 0)),
            defeats=int(row.get("derrotas", 0)),
            gp=int(row.get("gols_pro", 0)),
            gc=int(row.get("gols_contra", 0)),
            sg=int(row.get("saldo_gols", 0)),
            pontos=int(row.get("pontos", 0)),
            temporada=temporada,
        )

    def get_all(self, temporada: Optional[str] = None) -> List[ClassificacaoBase]:
        """Retorna toda a classificação básica."""
        df = self._load_data()

        if df.empty:
            return []

        return [self._row_to_entity(row, temporada) for _, row in df.iterrows()]

    def get_by_posicao(
        self, posicao: int, temporada: Optional[str] = None
    ) -> Optional[ClassificacaoBase]:
        """Retorna a classificação de um time pela posição."""
        df = self._load_data()

        if df.empty:
            return None

        filtered = df[df.get("posicao") == posicao]

        if filtered.empty:
            return None

        return self._row_to_entity(filtered.iloc[0], temporada)

    def get_by_time(
        self, nome_time: str, temporada: Optional[str] = None
    ) -> Optional[ClassificacaoBase]:
        """Retorna a classificação de um time pelo nome."""
        df = self._load_data()

        if df.empty:
            return None

        return self._row_to_entity(filtered.iloc[0], temporada)

    def get_times_rebaixados(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoBase]:
        """Retorna os times na zona de rebaixamento."""
        df = self._load_data()
        if df.empty:
            return []
        filtered = df[df.get("posicao", 0) >= 17]
        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]

    def get_times_liberadores(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoBase]:
        """Retorna os times na zona de Libertadores."""
        df = self._load_data()
        if df.empty:
            return []
        filtered = df[df.get("posicao", 0) <= 6]
        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]
