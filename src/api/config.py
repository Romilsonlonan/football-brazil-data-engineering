"""Configurações da API."""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class APIConfig:
    """Configurações gerais da API."""

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: list = None

    # Segurança
    api_key: Optional[str] = None

    # Observabilidade
    enable_metrics: bool = True

    # Dados
    data_path: str = "./data"

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Cria configuração a partir de variáveis de ambiente."""
        return cls(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            debug=os.getenv("API_DEBUG", "false").lower() == "true",
            api_key=os.getenv("API_KEY"),
            data_path=os.getenv("DATA_PATH", "./data"),
            enable_metrics=os.getenv("API_ENABLE_METRICS", "true").lower() == "true",
        )


# Instância global de configuração
config = APIConfig.from_env()
