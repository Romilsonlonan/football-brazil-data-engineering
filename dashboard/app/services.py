from typing import Optional
from pandas import DataFrame

from dashboard.application.use_cases.buscar_classificacao import BuscarClassificacaoUseCase
from dashboard.application.use_cases.buscar_elenco import BuscarElencoUseCase
from dashboard.infrastructure.repositories.parquet_repository import ParquetRepository
from dashboard.shared.config import get_data_path, get_bronze_data_path


class DashboardService:
    _classificacao_use_case: Optional[BuscarClassificacaoUseCase] = None
    _elenco_use_case: Optional[BuscarElencoUseCase] = None
    _times_cache: Optional[list[str]] = None
    _classificacao_cache: Optional[DataFrame] = None

    @classmethod
    def get_classificacao_use_case(cls) -> BuscarClassificacaoUseCase:
        if cls._classificacao_use_case is None:
            repo = ParquetRepository(get_data_path())
            cls._classificacao_use_case = BuscarClassificacaoUseCase(repo)
        return cls._classificacao_use_case

    @classmethod
    def get_elenco_use_case(cls) -> BuscarElencoUseCase:
        if cls._elenco_use_case is None:
            repo = ParquetRepository(get_bronze_data_path())
            cls._elenco_use_case = BuscarElencoUseCase(repo)
        return cls._elenco_use_case

    @classmethod
    def get_classificacao_df(cls) -> DataFrame:
        if cls._classificacao_cache is None:
            try:
                cls._classificacao_cache = cls.get_classificacao_use_case().execute()
            except Exception as e:
                print(f"[DashboardService] Erro ao carregar classificação: {e}")
                cls._classificacao_cache = DataFrame()
        return cls._classificacao_cache

    @classmethod
    def get_times(cls) -> list[str]:
        if cls._times_cache is None:
            try:
                cls._times_cache = cls.get_elenco_use_case().get_times()
            except Exception as e:
                print(f"[DashboardService] Erro ao carregar times: {e}")
                cls._times_cache = []
        return cls._times_cache

    @classmethod
    def clear_cache(cls) -> None:
        cls._classificacao_cache = None
