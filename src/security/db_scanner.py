"""
Scanner de Banco de Dados para PII - Lakehouse Brasileiro
=========================================================

Este módulo implementa detecção de PII em bancos de dados usando Piicatcher.

Referências:
- Piicatcher: https://piicatcher.io/

Instalação:
    pip install piicatcher

Usage:
    from src.security.db_scanner import DatabaseScanner
    
    scanner = DatabaseScanner()
    results = scanner.scan_connection("postgresql://user:pass@localhost/dbname")
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

from src.utils.logger import logger


@dataclass
class TableScanResult:
    """Resultado do scan de uma tabela."""
    table_name: str
    has_pii: bool
    pii_types: List[str]
    columns_with_pii: List[Dict[str, Any]]


@dataclass
class DatabaseScanResult:
    """Resultado do scan completo do banco."""
    database_name: str
    scan_time: datetime
    tables_scanned: int
    tables_with_pii: int
    results: List[TableScanResult]
    
    @property
    def has_pii(self) -> bool:
        return self.tables_with_pii > 0
    
    def to_dict(self) -> Dict:
        return {
            "database_name": self.database_name,
            "scan_time": self.scan_time.isoformat(),
            "tables_scanned": self.tables_scanned,
            "tables_with_pii": self.tables_with_pii,
            "has_pii": self.has_pii,
            "tables": [
                {
                    "table_name": r.table_name,
                    "has_pii": r.has_pii,
                    "pii_types": r.pii_types,
                    "columns": r.columns_with_pii
                }
                for r in self.results
            ]
        }


class DatabaseScanner:
    """
    Scanner de PII para bancos de dados.
    
    Suporta:
    - PostgreSQL
    - MySQL/MariaDB
    - SQLite
    - Snowflake
    - AWS Athena
    
    Example:
        >>> scanner = DatabaseScanner()
        >>> result = scanner.scan_connection(\n        ...     "postgresql://user:pass@localhost:5432/lakehouse\"\n        ... )\n        >>> print(f"Tabelas com PII: {result.tables_with_pii}")
    """
    
    PII_TYPES = [
        "EMAIL",
        "PHONE",
        "CREDIT_CARD",
        "DATE_OF_BIRTH",
        "GENDER",
        "LOCATION",
        "NAME",
        "SSN",
        "IP_ADDRESS",
        "PASSWORD",
        "URL",
        "ADDRESS",
    ]
    
    def __init__(self):
        logger.info("🔍 DatabaseScanner inicializado")
    
    def scan_connection(
        self,
        connection_string: str,
        catalog: Optional[str] = None,
        schema: Optional[str] = None
    ) -> DatabaseScanResult:
        """
        Escaneia um banco de dados via connection string.
        
        Args:
            connection_string: String de conexão (URI)
            catalog: Catálogo específico (opcional)
            schema: Schema específico (opcional)
            
        Returns:
            DatabaseScanResult com os resultados
        """
        logger.info("=" * 60)
        logger.info(f"🔍 ESCANEANDO BANCO DE DADOS")
        logger.info(f"   Connection: {self._mask_connection(connection_string)}")
        logger.info("=" * 60)
        
        try:
            from piicatcher import scan_database
            
            # Extrair nome do banco
            db_name = self._extract_db_name(connection_string)
            
            # Executar scan
            scan_result = scan_database(connection_string)
            
            # Processar resultados
            results = []
            tables_with_pii = 0
            
            for table in scan_result.get("tables", []):
                table_result = TableScanResult(
                    table_name=table.get("name", "unknown"),
                    has_pii=table.get("has_pii", False),
                    pii_types=table.get("pii_types", []),
                    columns_with_pii=[
                        col for col in table.get("columns", [])
                        if col.get("has_pii", False)
                    ]
                )
                
                if table_result.has_pii:
                    tables_with_pii += 1
                    logger.warning(
                        f"   📍 Tabela '{table_result.table_name}' contém PII: "
                        f"{', '.join(table_result.pii_types)}"
                    )
                
                results.append(table_result)
            
            db_result = DatabaseScanResult(
                database_name=db_name,
                scan_time=datetime.now(),
                tables_scanned=len(results),
                tables_with_pii=tables_with_pii,
                results=results
            )
            
            # Log resumo
            logger.info("=" * 60)
            if db_result.has_pii:
                logger.critical(
                    f"🚨 ALERTA: {tables_with_pii} tabelas com dados sensíveis!"
                )
            else:
                logger.info("✅ Nenhum PII detectado no banco de dados")
            logger.info(f"   Total de tabelas: {db_result.tables_scanned}")
            logger.info("=" * 60)
            
            return db_result
            
        except ImportError:
            logger.error("⚠️ Piicatcher não instalado")
            logger.info("   Execute: pip install piicatcher")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao escanear banco: {e}")
            raise
    
    def scan_table(
        self,
        connection_string: str,
        table_name: str,
        schema: Optional[str] = None
    ) -> TableScanResult:
        """Escaneia uma tabela específica."""
        logger.info(f"🔍 Escaneando tabela: {table_name}")
        
        # Implementação simplificada - em produção usaria API do Piicatcher
        result = self.scan_connection(connection_string)
        
        for table in result.results:
            if table.table_name == table_name:
                return table
        
        return TableScanResult(
            table_name=table_name,
            has_pii=False,
            pii_types=[],
            columns_with_pii=[]
        )
    
    def _mask_connection(self, conn_str: str) -> str:
        """Mascara credenciais na string de conexão."""
        import re
        
        # Substitui senha por ***
        masked = re.sub(
            r'(://[^:]+:)[^@]+(@)',
            r'\1***\2',
            conn_str
        )
        return masked
    
    def _extract_db_name(self, conn_str: str) -> str:
        """Extrai nome do banco da string de conexão."""
        import re
        
        match = re.search(r'/([^/?]+)', conn_str)
        if match:
            return match.group(1)
        
        # SQLite
        match = re.search(r'SQLite[/\\](.+)', conn_str)
        if match:
            return match.group(1)
        
        return "unknown"


def scan_database_security(connection_string: str, db_name: str = None) -> DatabaseScanResult:
    """
    Função helper para escanear banco de dados.
    
    Args:
        connection_string: String de conexão
        db_name: Nome do banco (opcional)
        
    Returns:
        DatabaseScanResult
    """
    scanner = DatabaseScanner()
    return scanner.scan_connection(connection_string)
