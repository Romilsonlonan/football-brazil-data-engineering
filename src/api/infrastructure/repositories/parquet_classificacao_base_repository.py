"""Repositório para ler dados do arquivo Parquet (classificação básica).

Este repositório lê dados do arquivo gold/classificacao.parquet (sem vagas).
"""

import pandas as pd
from pathlib import Path
from typing import List, Optional

import os

from src.api.domain.entities.classificacao_base import ClassificacaoBase
from src.api.domain.entities.time import Time
from src.api.domain.repositories.interface import IClassificacaoRepository


class ParquetClassificacaoBaseRepository(IClassificacaoRepository):
    """Repositório que lê dados do arquivo Parquet Gold básico."""

    def __init__(self, parquet_path: Optional[Path] = None):
        """
        Inicializa o repositório.

        Args:
            parquet_path: Caminho para o arquivo parquet.
                          Se None, usa o caminho padrão.
        """
        if parquet_path is None:
            # Caminho padrão para o arquivo gold básico
            data_path = os.environ.get("DATA_PATH", "/app/data")
            parquet_path = Path(f"{data_path}/gold/classificacao.parquet")

        self._parquet_path = parquet_path
        self._df: Optional[pd.DataFrame] = None

    def _load_data(self) -> pd.DataFrame:
        """Carrega os dados do arquivo parquet."""
        if self._df is None:
            if self._parquet_path.exists():
                self._df = pd.read_parquet(self._parquet_path)
            else:
                # Retorna DataFrame vazio se arquivo não existir
                self._df = pd.DataFrame(
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

        filtered = df[df.get("time", "").str.lower() == nome_time.lower()]

        if filtered.empty:
            return None

        return self._row_to_entity(filtered.iloc[0], temporada)
