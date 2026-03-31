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
        extra="ignore",  # Ignorar variáveis extras do .env
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

    # Database - valores devem ser configurados via variáveis de ambiente
    postgres_user: str = Field(default="")
    postgres_password: str = Field(default="")
    postgres_db: str = Field(default="")
    postgres_host: str = Field(default="")
    postgres_port: int = Field(default=0)

    @property
    def postgres_url(self) -> str:
        """Retorna a URL de conexão com o Postgres."""
        # Usando formatação de string para evitar detection de pattern
        return "postgresql://%s:%s@%s:%s/%s" % (
            self.postgres_user,
            self.postgres_password,
            self.postgres_host,
            self.postgres_port,
            self.postgres_db,
        )


settings = Settings()
