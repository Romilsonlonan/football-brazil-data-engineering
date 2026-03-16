# ============================================
# Security Module - Lakehouse Brasileiro
# ============================================
# Módulo de segurança e observabilidade de dados

# Imports lazy para evitar erros quando dependências não estão instaladas

def __getattr__(name):
    """Importação lazy para módulos opcionais."""
    # Credentials Scanner
    if name == "CredentialsScanner":
        from src.security.credentials_scanner import CredentialsScanner
        return CredentialsScanner
    elif name == "CredentialsScanResult":
        from src.security.credentials_scanner import CredentialsScanResult
        return CredentialsScanResult
    elif name == "CredentialFinding":
        from src.security.credentials_scanner import CredentialFinding
        return CredentialFinding
    elif name == "scan_env_files":
        from src.security.credentials_scanner import scan_env_files
        return scan_env_files
    elif name == "scan_config_files":
        from src.security.credentials_scanner import scan_config_files
        return scan_config_files
    
    # Data Scanner (Presidio)
    elif name == "DataSecurityScanner":
        from src.security.data_scanner import DataSecurityScanner
        return DataSecurityScanner
    elif name == "SecurityScanResult":
        from src.security.data_scanner import SecurityScanResult
        return SecurityScanResult
    
    # Database Scanner (Piicatcher)
    elif name == "DatabaseScanner":
        from src.security.db_scanner import DatabaseScanner
        return DatabaseScanner
    elif name == "DatabaseScanResult":
        from src.security.db_scanner import DatabaseScanResult
        return DatabaseScanResult
    
    # Log Observer
    elif name == "LogObserver":
        from src.security.log_observer import LogObserver
        return LogObserver
    elif name == "PipelineMonitor":
        from src.security.log_observer import PipelineMonitor
        return PipelineMonitor
    elif name == "get_monitor":
        from src.security.log_observer import get_monitor
        return get_monitor
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Credentials Scanner
    "CredentialsScanner",
    "CredentialsScanResult", 
    "CredentialFinding",
    "scan_env_files",
    "scan_config_files",
    # Data Scanner (Presidio)
    "DataSecurityScanner",
    "SecurityScanResult",
    # Database Scanner (Piicatcher)
    "DatabaseScanner",
    "DatabaseScanResult",
    # Log Observer
    "LogObserver", 
    "PipelineMonitor",
    "get_monitor",
]
