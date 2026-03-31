"""Configurações do Dashboard - Shared Layer"""
from functools import lru_cache


@lru_cache
def get_page_config() -> dict:
    """Retorna a configuração da página."""
    return {
        "page_title": "Dashboard Brasileirão",
        "page_icon": "⚽",
        "layout": "wide",
    }


def get_data_path() -> str:
    """Retorna o caminho base dos dados."""
    return "data/gold"


def get_bronze_data_path() -> str:
    """Retorna o caminho base dos dados bronze."""
    return "data/bronze"