from typing import Any, Dict, List, Optional
from src.infrastructure.metadata.interfaces import MetadataService
from src.utils.logger import logger

class MemoryMetadataService(MetadataService):
    """
    Implementação em memória do MetadataService para desenvolvimento e testes.
    """

    def __init__(self):
        self._tables: Dict[str, Dict[str, Any]] = {}
        logger.info("🧠 MemoryMetadataService inicializado")

    def register_table(self, table_name: str, schema: Dict[str, str], descriptions: Optional[Dict[str, str]] = None) -> None:
        self._tables[table_name] = {
            "schema": schema,
            "descriptions": descriptions or {}
        }
        logger.info(f"📝 Tabela '{table_name}' registrada no MemoryMetadataService")

    def get_table_metadata(self, table_name: str) -> Optional[Dict[str, Any]]:
        return self._tables.get(table_name)

    def search_metadata(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Busca simples por substring (substituindo RAG por enquanto).
        """
        logger.info(f"🔍 Pesquisando metadados para: '{query}'")
        results = []
        query_lower = query.lower()

        for table_name, metadata in self._tables.items():
            # Verifica nome da tabela
            if query_lower in table_name.lower():
                results.append({"table_name": table_name, "metadata": metadata, "score": 1.0})
                continue

            # Verifica descrições de colunas
            for col_name, desc in metadata["descriptions"].items():
                if query_lower in desc.lower() or query_lower in col_name.lower():
                    results.append({"table_name": table_name, "column": col_name, "metadata": metadata, "score": 0.8})
                    break

        # Ordena por score e limita ao top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
