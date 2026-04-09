"""Repositório para ler dados do arquivo Parquet (classificação com vagas).

Este repositório lê dados do arquivo gold/classificacao-vagas.parquet do MinIO.
"""

import pandas as pd
from typing import List, Optional

from src.api.domain.entities.classificacao_vagas import ClassificacaoVagas
from src.api.domain.entities.time import Time
from src.api.domain.repositories.interface import IClassificacaoRepository
from src.api.infrastructure.repositories.minio_mixin import MinIODataFrameMixin


class ParquetClassificacaoVagasRepository(
    IClassificacaoRepository, MinIODataFrameMixin
):
    """Repositório que lê dados do arquivo Parquet Gold com vagas do MinIO."""

    def __init__(self, parquet_path: Optional[str] = None):
        """
        Inicializa o repositório.

        Args:
            parquet_path: Caminho para o arquivo parquet (descontinuado, usa MinIO).
        """
        self._folder = "gold"
        self._filename = "classificacao-vagas.parquet"
        self._df: Optional[pd.DataFrame] = None

    def _load_data(self) -> pd.DataFrame:
        """Carrega os dados do MinIO."""
        if self._df is None:
            self._df = self._load_from_minio(self._folder, self._filename)
        return self._df

    def _row_to_entity(
        self, row: pd.Series, temporada: Optional[str] = None
    ) -> ClassificacaoVagas:
        """Converte uma linha do DataFrame para entidade ClassificacaoVagas."""
        time_nome = row.get("time", "")
        time = Time(nome=str(time_nome))

        return ClassificacaoVagas(
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
            zona=row.get("zona", ""),
            status_curto=row.get("status_curto", ""),
            temporada=temporada,
        )

    def get_all(self, temporada: Optional[str] = None) -> List[ClassificacaoVagas]:
        """Retorna toda a classificação com vagas."""
        df = self._load_data()

        if df.empty:
            return []

        return [self._row_to_entity(row, temporada) for _, row in df.iterrows()]

    def get_by_posicao(
        self, posicao: int, temporada: Optional[str] = None
    ) -> Optional[ClassificacaoVagas]:
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
    ) -> Optional[ClassificacaoVagas]:
        """Retorna a classificação de um time pelo nome."""
        df = self._load_data()

        if df.empty:
            return None

        filtered = df[df.get("time", "").str.lower() == nome_time.lower()]

        if filtered.empty:
            return None

        return self._row_to_entity(filtered.iloc[0], temporada)

    def get_by_zona(
        self, zona: str, temporada: Optional[str] = None
    ) -> List[ClassificacaoVagas]:
        """Retorna todos os times de uma zona específica."""
        df = self._load_data()

        if df.empty:
            return []

        filtered = df[df.get("zona") == zona]

        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]

    def get_libertadores(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoVagas]:
        """Retorna times classificados para Libertadores."""
        df = self._load_data()

        if df.empty:
            return []

        filtered = df[df.get("zona", "").str.contains("LIBERTADORES")]

        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]

    def get_sul_americana(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoVagas]:
        """Retorna times classificados para Sul-Americana."""
        df = self._load_data()

        if df.empty:
            return []

        filtered = df[df.get("zona", "").str.contains("SUL-AMERICANA")]

        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]

    def get_rebaixados(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoVagas]:
        """Retorna times rebaixados."""
        df = self._load_data()

        if df.empty:
            return []

        filtered = df[df.get("zona", "").str.contains("REBAIXAMENTO")]

        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]

    def get_times_rebaixados(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoVagas]:
        """Retorna os times na zona de rebaixamento."""
        return self.get_rebaixados(temporada)

    def get_times_liberadores(
        self, temporada: Optional[str] = None
    ) -> List[ClassificacaoVagas]:
        """Retorna os times na zona de Libertadores."""
        return self.get_libertadores(temporada)
