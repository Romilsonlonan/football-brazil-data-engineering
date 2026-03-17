"""Configurações do projeto."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Paths
    bronze_path: Path = Field(default=Path("data/bronze"))
    """Caminho para dados da camada Bronze."""

    silver_path: Path = Field(default=Path("data/silver"))
    """Caminho para dados da camada Silver."""

    gold_path: Path = Field(default=Path("data/gold"))
    """Caminho para dados da camada Gold."""

    # API
    api_key: str = Field(default="")
    """Chave da API para serviços externos."""

    # Airflow
    airflow_uid: str = Field(default="50000")
    """UID do usuário Airflow."""

    airflow_gid: str = Field(default="0")
    """GID do usuário Airflow."""

    # Superset
    superset_secret_key: str = Field(default="")
    """Chave secreta do Superset."""


settings = Settings()
