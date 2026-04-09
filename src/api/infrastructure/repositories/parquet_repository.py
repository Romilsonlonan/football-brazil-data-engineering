"""Repositório para ler dados do arquivo Parquet (silver-classificacao-tratado)."""

import pandas as pd
from typing import List, Optional

from src.api.domain.entities.classificacao import Classificacao
from src.api.domain.entities.time import Time
from src.api.domain.entities.vagas import VagasConfig
from src.api.domain.repositories.interface import IClassificacaoRepository
from src.api.infrastructure.repositories.minio_mixin import MinIODataFrameMixin


class ParquetClassificacaoRepository(IClassificacaoRepository, MinIODataFrameMixin):
    """Repositório que lê dados do arquivo Parquet tratado do MinIO."""

    def __init__(self, parquet_path: Optional[str] = None):
        """
        Inicializa o repositório.

        Args:
            parquet_path: Caminho para o arquivo parquet (descontinuado, usa MinIO).
        """
        self._folder = "silver"
        self._filename = "classificacao-limpa.parquet"
        self._df: Optional[pd.DataFrame] = None

    def _load_data(self) -> pd.DataFrame:
        """Carrega os dados do MinIO."""
        if self._df is None:
            self._df = self._load_from_minio(self._folder, self._filename)
        return self._df

    def _row_to_entity(
        self, row: pd.Series, temporada: Optional[str] = None
    ) -> Classificacao:
        """Converte uma linha do DataFrame para entidade Classificacao."""
        # Extrai o nome do time
        time_nome = row.get("Time", row.get("time", ""))

        # Cria a entidade Time
        time = Time(nome=str(time_nome))

        # Cria a entidade Classificacao
        classificacao = Classificacao(
            posicao=int(row.get("Posição", row.get("posicao", 0))),
            time=time,
            jogos=int(row.get("Jogos", row.get("jogos", 0))),
            vitorias=int(row.get("Vitorias", row.get("vitorias", 0))),
            empates=int(row.get("Empates", row.get("empates", 0))),
            derrotas=int(row.get("Derrotas", row.get("derrotas", 0))),
            gp=int(row.get("GolsPro", row.get("gp", 0))),
            gc=int(row.get("GolsContra", row.get("gc", 0))),
            sg=int(row.get("SaldoGols", row.get("sg", 0))),
            pontos=int(row.get("Pontos", row.get("pontos", 0))),
            temporada=temporada,
        )

        return classificacao

    def get_all(self, temporada: Optional[str] = None) -> List[Classificacao]:
        """Retorna toda a classificação."""
        df = self._load_data()

        if df.empty:
            return []

        return [self._row_to_entity(row, temporada) for _, row in df.iterrows()]

    def get_by_posicao(
        self, posicao: int, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """Retorna a classificação de um time pela posição."""
        df = self._load_data()

        if df.empty:
            return None

        filtered = df[df.get("Posição", df.get("posicao", pd.Series())) == posicao]

        if filtered.empty:
            return None

        return self._row_to_entity(filtered.iloc[0], temporada)

    def get_by_time(
        self, nome_time: str, temporada: Optional[str] = None
    ) -> Optional[Classificacao]:
        """Retorna a classificação de um time pelo nome."""
        df = self._load_data()

        if df.empty:
            return None

        # Normaliza nomes para comparação
        nome_normalizado = nome_time.lower().strip()

        filtered = df[
            df.get("Time", df.get("time", pd.Series())).str.lower().str.strip()
            == nome_normalizado
        ]

        if filtered.empty:
            return None

        return self._row_to_entity(filtered.iloc[0], temporada)

    def get_times_rebaixados(
        self, temporada: Optional[str] = None
    ) -> List[Classificacao]:
        """Retorna os times na zona de rebaixamento."""
        df = self._load_data()

        if df.empty:
            return []

        posicao_col = "Posição" if "Posição" in df.columns else "posicao"

        filtered = df[df[posicao_col] >= 17]

        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]

    def get_times_liberadores(
        self, temporada: Optional[str] = None
    ) -> List[Classificacao]:
        """Retorna os times na zona de Libertadores."""
        df = self._load_data()

        if df.empty:
            return []

        posicao_col = "Posição" if "Posição" in df.columns else "posicao"

        filtered = df[df[posicao_col] <= 5]

        return [self._row_to_entity(row, temporada) for _, row in filtered.iterrows()]

    def get_vagas_config(self, temporada: str = "2026") -> VagasConfig:
        """Retorna a configuração de vagas para a temporada."""
        return VagasConfig(
            temporada=temporada,
            vagas_libertadores_grupo=4,
            vagas_libertadores_pre=1,
            vagas_sul_americana=6,
            rebaixados=4,
        )

    def get_dados_completos(self, temporada: str = "2026") -> dict:
        """
        Retorna os dados completos incluindo configuração de vagas.

        Args:
            temporada: Ano da temporada

        Returns:
            Dicionário com classificação e configurações
        """
        classificacao = self.get_all(temporada)
        vagas_config = self.get_vagas_config(temporada)

        # Adiciona status a cada classificação
        for c in classificacao:
            c.pontos = c.pontos  # Garante que está calculado

        return {
            "temporada": temporada,
            "classificacao": classificacao,
            "vagas": vagas_config.to_dict(),
            "total_times": len(classificacao),
        }
