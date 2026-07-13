from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class MetadataService(ABC):
    """
    Interface para o serviço de metadados do Lakehouse.
    Permite registrar, consultar e pesquisar metadados das tabelas.
    """

    @abstractmethod
    def register_table(self, table_name: str, schema: Dict[str, str], descriptions: Optional[Dict[str, str]] = None) -> None:
        """
        Registra o esquema de uma tabela e suas descrições.
        """
        pass

    @abstractmethod
    def get_table_metadata(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Recupera os metadados de uma tabela específica.
        """
        pass

    @abstractmethod
    def search_metadata(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Pesquisa metadados usando busca semântica (RAG).
        """
        pass
