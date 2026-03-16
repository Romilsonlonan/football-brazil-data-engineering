# ============================================
# Security Module - Lakehouse Brasileiro
# ============================================
# Módulo de segurança e observabilidade de dados

from src.security.credentials_scanner import (
    CredentialsScanner,
    CredentialsScanResult,
    CredentialFinding,
    scan_env_files,
    scan_config_files,
)
from src.security.data_scanner import DataSecurityScanner, SecurityScanResult
from src.security.log_observer import LogObserver, PipelineMonitor, get_monitor
from src.security.db_scanner import DatabaseScanner, DatabaseScanResult

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
