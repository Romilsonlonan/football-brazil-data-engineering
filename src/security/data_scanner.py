"""
Scanner de Segurança de Dados - Lakehouse Brasileiro
=====================================================

Este módulo implementa a detecção de dados sensíveis (PII) usando
o Microsoft Presidio para proteção de dados em pipelines.

Referências:
- Microsoft Presidio: https://microsoft.github.io/presidio/
- PII Detection: https://learn.microsoft.com/en-us/azure/ai-services/presidio/

Instalação:
    pip install presidio-analyzer presidio-anonymizer spacy
    python -m spacy download pt_core_news_lg

Usage:
    from src.security.data_scanner import DataSecurityScanner
    
    scanner = DataSecurityScanner()
    result = scanner.scan_dataframe(df, "minha_tabela")
"""

from typing import Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from src.utils.logger import logger

# Tentar importar presidio_analyzer - pode não estar disponível em ambiente de desenvolvimento
try:
    from presidio_analyzer import AnalyzerEngine, PatternRecognizer
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    AnalyzerEngine = None
    PatternRecognizer = None

# Tentar importar presidio_anonymizer
try:
    from presidio_anonymizer import AnonymizerEngine
except ImportError:
    AnonymizerEngine = None


@dataclass
class SecurityFinding:
    """Representa uma descoberta de dados sensíveis."""
    table: str
    column: str
    row: int
    entity_type: str
    start: int
    end: int
    score: float
    text: str
    severity: str = "high"
    
    def to_dict(self) -> Dict:
        return {
            "table": self.table,
            "column": self.column,
            "row": self.row,
            "entity_type": self.entity_type,
            "start": self.start,
            "end": self.end,
            "score": round(self.score, 2),
            "text": self.text,
            "severity": self.severity
        }


@dataclass
class SecurityScanResult:
    """Resultado do scan de segurança."""
    table_name: str
    scan_time: datetime
    total_rows: int
    columns_scanned: int
    risks_found: int
    findings: List[SecurityFinding] = field(default_factory=list)
    
    @property
    def has_risks(self) -> bool:
        return self.risks_found > 0
    
    def to_dict(self) -> Dict:
        return {
            "table_name": self.table_name,
            "scan_time": self.scan_time.isoformat(),
            "total_rows": self.total_rows,
            "columns_scanned": self.columns_scanned,
            "risks_found": self.risks_found,
            "has_risks": self.has_risks,
            "findings": [f.to_dict() for f in self.findings]
        }


class DataSecurityScanner:
    """
    Scanner de segurança de dados com detecção de PII.
    
    Este scanner identifica:
    - CPF brasileiro
    - Telefones brasileiros
    - Endereços de email
    - Nomes de pessoas
    - Localizações
    - Dados financeiros
    
    Example:
        >>> scanner = DataSecurityScanner()
        >>> result = scanner.scan_dataframe(df, "classificacao")
        >>> if result.has_risks:
        ...     print(f"Riscos encontrados: {result.risks_found}")
    """
    
    # Entidades padrão do Presidio
    DEFAULT_ENTITIES = [
        "PERSON",
        "LOCATION",
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "DATE_TIME",
        "IBAN_CODE",
        "CRYPTO",
        "URL",
    ]
    
    # Entidades customizadas para Brasil
    BR_ENTITIES = [
        "BR_CPF",
        "BR_CNPJ",
        "BR_PHONE",
        "BR_PIS",
        "BR_CNH",
    ]
    
    def __init__(self, language: str = "pt"):
        """
        Inicializa o scanner de segurança.
        
        Args:
            language: Idioma para análise NLP (padrão: 'pt' para português)
        
        Raises:
            ImportError: Se presidio-analyzer não estiver instalado
        """
        if not PRESIDIO_AVAILABLE:
            raise ImportError(
                "presidio-analyzer não está instalado. "
                "Execute: pip install presidio-analyzer presidio-anonymizer spacy "
                "python -m spacy download pt_core_news_lg"
            )
        
        self.language = language
        self._setup_nlp_engine()
        self._setup_custom_recognizers()
        
        logger.info(f"🔒 DataSecurityScanner inicializado para idioma: {language}")
    
    def _setup_nlp_engine(self):
        """Configura o motor NLP para português."""
        try:
            # Usa NlpEngineProvider para configuração explícita do modelo spacy
            from presidio_analyzer.nlp_engine import NlpEngineProvider
            
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "pt", "model_name": "pt_core_news_lg"}]
            }
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()
            self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
            logger.info("✅ NLP Engine (spacy) configurado com modelo pt_core_news_lg")
        except Exception as e:
            logger.warning(f"⚠️ Spacy não disponível, usando padrão: {e}")
            self.analyzer = AnalyzerEngine()
    
    def _setup_custom_recognizers(self):
        """Adiciona reconhecedores customizados para dados brasileiros."""
        try:
            # CPF brasileiro
            cpf_recognizer = PatternRecognizer(
                supported_entity="BR_CPF",
                patterns=[
                    r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
                    r"\d{11}"
                ],
                name="Brazilian CPF",
                supported_language="pt"
            )
            
            # CNPJ brasileiro
            cnpj_recognizer = PatternRecognizer(
                supported_entity="BR_CNPJ",
                patterns=[
                    r"\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}",
                    r"\d{14}"
                ],
                name="Brazilian CNPJ",
                supported_language="pt"
            )
            
            # Telefone brasileiro
            phone_recognizer = PatternRecognizer(
                supported_entity="BR_PHONE",
                patterns=[
                    r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}",
                    r"\d{10,11}",
                    r"\+55\s?\d{2}\s?\d{4,5}\s?\d{4}"
                ],
                name="Brazilian Phone",
                supported_language="pt"
            )
            
            # PIS brasileiro
            pis_recognizer = PatternRecognizer(
                supported_entity="BR_PIS",
                patterns=[
                    r"\d{3}\.?\d{5}\.?\d{2}-?\d{1}"
                ],
                name="Brazilian PIS",
                supported_language="pt"
            )
            
            # CNH brasileira
            cnh_recognizer = PatternRecognizer(
                supported_entity="BR_CNH",
                patterns=[
                    r"\d{11}"
                ],
                name="Brazilian CNH",
                supported_language="pt"
            )
            
            # Registro de reconhecedores
            self.analyzer.registry.add_recognizer(cpf_recognizer)
            self.analyzer.registry.add_recognizer(cnpj_recognizer)
            self.analyzer.registry.add_recognizer(phone_recognizer)
            self.analyzer.registry.add_recognizer(pis_recognizer)
            self.analyzer.registry.add_recognizer(cnh_recognizer)
            
            logger.info("✅ Reconhecedores customizados registrados (CPF, CNPJ, Telefone, PIS, CNH)")
            
        except ImportError:
            logger.warning("⚠️ Presidio PatternRecognizer não disponível")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar reconhecedores: {e}")
    
    def scan_dataframe(
        self, 
        df: pd.DataFrame, 
        table_name: str,
        entities: Optional[List[str]] = None,
        log_findings: bool = True
    ) -> SecurityScanResult:
        """
        Escaneia um DataFrame em busca de dados sensíveis.
        
        Args:
            df: DataFrame para escanear
            table_name: Nome da tabela (para logs)
            entities: Lista de entidades para detectar (None = usar padrão)
            log_findings: Se deve gerar logs de alertas
            
        Returns:
            SecurityScanResult com os resultados do scan
        """
        entities = entities or (self.DEFAULT_ENTITIES + self.BR_ENTITIES)
        
        logger.info("=" * 60)
        logger.info(f"🔍 ESCANEANDO SEGURANÇA - Tabela: {table_name}")
        logger.info(f"   Linhas: {len(df)}, Colunas: {len(df.columns)}")
        logger.info("=" * 60)
        
        result = SecurityScanResult(
            table_name=table_name,
            scan_time=datetime.now(),
            total_rows=len(df),
            columns_scanned=len(df.columns),
            risks_found=0,
            findings=[]
        )
        
        # Escaneia cada coluna
        for column in df.columns:
            column_findings = self._scan_column(df[column], column, table_name, entities)
            result.findings.extend(column_findings)
        
        result.risks_found = len(result.findings)
        
        # Gerar alertas
        if log_findings:
            self._log_findings(result)
        
        return result
    
    def _scan_column(
        self, 
        series: pd.Series, 
        column_name: str, 
        table_name: str,
        entities: List[str]
    ) -> List[SecurityFinding]:
        """Escaneia uma coluna específica."""
        findings = []
        
        # Detectar tipo da coluna para otimização
        if series.dtype == 'object':
            # Coluna de texto - escanear cada valor
            for idx, value in series.items():
                if pd.isna(value):
                    continue
                
                text = str(value)
                if len(text) < 3:  # Ignorar texto muito curto
                    continue
                
                try:
                    results = self.analyzer.analyze(
                        text=text,
                        language=self.language,
                        entities=entities,
                        score_threshold=0.5  # Threshold de confiança
                    )
                    
                    for res in results:
                        findings.append(SecurityFinding(
                            table=table_name,
                            column=column_name,
                            row=int(idx),
                            entity_type=res.entity_type,
                            start=res.start,
                            end=res.end,
                            score=res.score,
                            text=text[res.start:res.end],
                            severity=self._get_severity(res.entity_type)
                        ))
                except Exception as e:
                    logger.debug(f"Erro ao analisar '{column_name}': {e}")
        
        return findings
    
    def _get_severity(self, entity_type: str) -> str:
        """Determina a severidade baseada no tipo de entidade."""
        high_severity = ["BR_CPF", "BR_CNPJ", "BR_PIS", "BR_CNH", "CREDIT_CARD", "IBAN_CODE"]
        medium_severity = ["BR_PHONE", "EMAIL_ADDRESS", "PHONE_NUMBER"]
        
        if entity_type in high_severity:
            return "critical"
        elif entity_type in medium_severity:
            return "high"
        else:
            return "medium"
    
    def _log_findings(self, result: SecurityScanResult):
        """Gera logs formatados com os achados."""
        if result.has_risks:
            logger.critical("=" * 60)
            logger.critical(f"🚨 ALERTA DE SEGURANÇA: {result.risks_found} dados sensíveis detectados!")
            logger.critical("=" * 60)
            
            # Agrupar por tipo
            by_type: Dict[str, int] = {}
            for finding in result.findings:
                by_type[finding.entity_type] = by_type.get(finding.entity_type, 0) + 1
            
            for entity, count in by_type.items():
                logger.warning(f"   📍 {entity}: {count} ocorrências")
            
            # Detalhes dos primeiros 5
            logger.warning("   Primeiras detecções:")
            for i, finding in enumerate(result.findings[:5]):
                logger.warning(
                    f"      {i+1}. [{finding.severity.upper()}] "
                    f"{finding.entity_type} na coluna '{finding.column}', "
                    f"linha {finding.row}: '{finding.text[:20]}...'"
                )
            
            logger.critical("=" * 60)
            logger.critical("⚠️  AÇÃO NECESSÁRIA: Revise e anonimize os dados antes de prosseguir!")
            logger.critical("=" * 60)
        else:
            logger.info(f"✅ Scan concluído: Nenhum dado sensível detectado em {result.table_name}")
            logger.info(f"   Total de {result.total_rows} linhas verificadas em {result.columns_scanned} colunas")
    
    def anonymize_text(self, text: str, entities: Optional[List[str]] = None) -> str:
        """
        Anonimiza dados sensíveis em um texto.
        
        Args:
            text: Texto para anonimizar
            entities: Entidades para anonimizar
            
        Returns:
            Texto com dados sensíveis substituídos
        """
        if AnonymizerEngine is None:
            logger.error("presidio-anonymizer não está instalado")
            return text
        
        entities = entities or self.DEFAULT_ENTITIES
        
        try:
            analyzer_results = self.analyzer.analyze(
                text=text,
                language=self.language,
                entities=entities
            )
            
            anonymizer = AnonymizerEngine()
            anonymized = anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results
            )
            
            return anonymized.text
        except Exception as e:
            logger.error(f"Erro ao anonimizar texto: {e}")
            return text


def scan_pipeline_security(df: pd.DataFrame, pipeline_name: str) -> SecurityScanResult:
    """
    Função helper para integrar com pipelines existentes.
    
    Args:
        df: DataFrame do pipeline
        pipeline_name: Nome do pipeline
        
    Returns:
        SecurityScanResult com os resultados
    """
    scanner = DataSecurityScanner()
    return scanner.scan_dataframe(df, pipeline_name)


# ============================================
# Decorator para Scan Automático em Pipelines
# ============================================

def with_security_scan(table_name: str):
    """
    Decorador para executar scan de segurança automaticamente em pipelines.
    
    Usage:
        @with_security_scan("classificacao")
        def my_pipeline():
            df = load_data()
            process_data(df)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"🔒 Executando pipeline com verificação de segurança: {table_name}")
            
            # Executa o pipeline
            result = func(*args, **kwargs)
            
            # Se o resultado for um DataFrame, escaneia
            if isinstance(result, pd.DataFrame):
                scanner = DataSecurityScanner()
                scan_result = scanner.scan_dataframe(result, table_name)
                
                if scan_result.has_risks:
                    logger.critical(
                        f"🚨 Pipeline '{table_name}' contém dados sensíveis! "
                        f"Revise o resultado do scan."
                    )
            
            return result
        return wrapper
    return decorator
