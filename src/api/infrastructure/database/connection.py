"""Configurações de conexão com banco de dados."""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class DatabaseConfig:
    """Configuração do banco de dados."""

    host: str = "localhost"
    port: int = 5432
    database: str = "brasileirao"
    user: str = "postgres"
    password: str = ""

    # Para Supabase
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Cria configuração a partir de variáveis de ambiente."""
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "brasileirao"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
        )

    @property
    def connection_string(self) -> str:
        """Retorna string de conexão."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


# Instância global de configuração
db_config = DatabaseConfig.from_env()
