"""
Scanner de Credenciais - Lakehouse Brasileiro
==============================================

Este módulo implementa detecção de credenciais vazadas em arquivos
de configuração, variáveis de ambiente e código fonte.

Tipos de credenciais detectadas:
- AWS Access Keys e Secret Keys
- Azure Storage Keys e Connection Strings
- GCP API Keys
- Generic API Keys e Tokens
- Senhas em texto claro
- Connection Strings de banco de dados
- Private Keys (RSA, SSH, etc.)
- Tokens de autenticação (JWT, OAuth, etc.)

Usage:
    from src.security.credentials_scanner import CredentialsScanner
    
    scanner = CredentialsScanner()
    results = scanner.scan_file(".env")
    
    # Ou escanear diretório inteiro
    results = scanner.scan_directory(".")
"""

import os
import re
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from src.utils.logger import logger


# Patterns de credenciais conhecidas
CREDENTIAL_PATTERNS = {
    # AWS
    "AWS_ACCESS_KEY_ID": r"(?:aws_access_key_id|aws_access_key|AWS_ACCESS_KEY_ID)\s*[=:]\s*([A-Z0-9]{20})",
    "AWS_SECRET_ACCESS_KEY": r"(?:aws_secret_access_key|aws_secret_key|AWS_SECRET_ACCESS_KEY)\s*[=:]\s*([A-Za-z0-9/+=]{40})",
    "AWS_SESSION_TOKEN": r"(?:aws_session_token|AWS_SESSION_TOKEN)\s*[=:]\s*([A-Za-z0-9/+=]{200,})",
    
    # Azure
    "AZURE_STORAGE_KEY": r"(?:azure_storage_key|AZURE_STORAGE_KEY|AZURE_STORAGE_CONNECTION_STRING)\s*[=:]\s*([A-Za-z0-9+/=]{86,})",
    "AZURE_CLIENT_SECRET": r"(?:azure_client_secret|client_secret|AZURE_CLIENT_SECRET)\s*[=:]\s*([A-Za-z0-9\-_]{32,})",
    "AZURE_STORAGE_CONNECTION": r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+",
    
    # GCP
    "GCP_API_KEY": r"(?:gcp_api_key|google_api_key|GCP_API_KEY|AIza[0-9A-Za-z\-_]{35})",
    "GCP_SERVICE_ACCOUNT": r'"type": "service_account"',
    "GCP_PROJECT_ID": r'(?:gcp_project_id|project_id|GCP_PROJECT_ID)\s*[=:]\s*([a-z0-9\-]{6,30})',
    
    # Database
    "POSTGRES_CONNECTION": r"(?:postgres|postgresql)://[^\s]+",
    "MYSQL_CONNECTION": r"mysql://[^\s]+",
    "MONGODB_CONNECTION": r"mongodb(\+srv)?://[^\s]+",
    "REDIS_CONNECTION": r"redis://[^\s]+",
    "SQLALCHEMY_URL": r"sqlalchemy://[^\s]+",
    
    # Generic API Keys
    "API_KEY": r"(?:api_key|apikey|API_KEY|APIKEY)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?",
    "API_SECRET": r"(?:api_secret|apisecret|API_SECRET)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?",
    "ACCESS_TOKEN": r"(?:access_token|ACCESS_TOKEN)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})['\"]?",
    "REFRESH_TOKEN": r"(?:refresh_token|REFRESH_TOKEN)\s*[=:]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})['\"]?",
    
    # Tokens
    "JWT_TOKEN": r"eyJ[A-Za-z0-9\-_]+\.eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+",
    "GITHUB_TOKEN": r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}",
    "SLACK_TOKEN": r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9\-]*",
    "TWITTER_TOKEN": r"AAAA[A-Za-z0-9%]{30,}",
    
    # Private Keys
    "RSA_PRIVATE_KEY": r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
    "SSH_PRIVATE_KEY": r"-----BEGIN OPENSSH PRIVATE KEY-----",
    "PGP_PRIVATE_KEY": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
    
    # Generic Passwords (variáveis contendo password/pass/secret)
    "PASSWORD_VAR": r"(?:password|passwd|pwd|secret|PASSWORD|PASSWD|SECRET)\s*[=:]\s*['\"]?([^\s'\"]{8,})['\"]?",
    
    # Fernet Keys (Airflow)
    "FERNET_KEY": r"(?:fernet_key|FERNET_KEY)\s*[=:]\s*([A-Za-z0-9\-_]{44})",
    
    # Superset Secret Key
    "SUPERSET_SECRET_KEY": r"(?:superset_secret_key|SUPERSET_SECRET_KEY)\s*[=:]\s*['\"]?([a-f0-9]{64})['\"]?",
    
    # MinIO Keys
    "MINIO_ACCESS_KEY": r"(?:minio_access_key|MINIO_ACCESS_KEY)\s*[=:]\s*([a-zA-Z0-9]{10,})",
    "MINIO_SECRET_KEY": r"(?:minio_secret_key|MINIO_SECRET_KEY)\s*[=:]\s*([a-zA-Z0-9]{10,})",
}


# Extensões de arquivo para escanear
SCANNABLE_EXTENSIONS = {
    ".env", ".env.local", ".env.development", ".env.production",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".properties", ".conf", ".config",
    "credentials", ".pem", ".key"
}


# Arquivos/pastas para ignorar
IGNORED_PATHS = {
    ".git", ".venv", "venv", "env", "node_modules",
    "__pycache__", ".pytest_cache", "dist", "build",
    ".gitignore", ".dockerignore", "poetry.lock",
    "*.pyc", "*.pyo", "*.so"
}


@dataclass
class CredentialFinding:
    """Representa uma credencial detectada."""
    file_path: str
    line_number: int
    credential_type: str
    variable_name: str
    severity: str = "critical"
    
    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "credential_type": self.credential_type,
            "variable_name": self.variable_name,
            "severity": self.severity
        }


@dataclass
class CredentialsScanResult:
    """Resultado do scan de credenciais."""
    scan_path: str
    scan_time: datetime
    files_scanned: int
    credentials_found: int
    findings: List[CredentialFinding] = field(default_factory=list)
    
    @property
    def has_credentials(self) -> bool:
        return self.credentials_found > 0
    
    def to_dict(self) -> Dict:
        return {
            "scan_path": self.scan_path,
            "scan_time": self.scan_time.isoformat(),
            "files_scanned": self.files_scanned,
            "credentials_found": self.credentials_found,
            "has_credentials": self.has_credentials,
            "findings": [f.to_dict() for f in self.findings]
        }


class CredentialsScanner:
    """
    Scanner de credenciais vazadas.
    
    Example:
        >>> scanner = CredentialsScanner()
        >>> result = scanner.scan_file(".env")
        >>> if result.has_credentials:
        ...     print(f"Encontradas {result.credentials_found} credenciais!")
    """
    
    def __init__(self, severity_override: Optional[Dict[str, str]] = None):
        """
        Inicializa o scanner de credenciais.
        
        Args:
            severity_override: Sobrescrever severidade de tipos específicos
        """
        self.patterns = CREDENTIAL_PATTERNS
        self.severity_override = severity_override or {}
        
        # Compilar patterns para performance
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        for name, pattern in self.patterns.items():
            try:
                self._compiled_patterns[name] = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                logger.warning(f"⚠️ Pattern inválido para {name}: {e}")
        
        logger.info("🔐 CredentialsScanner inicializado")
    
    def scan_file(self, file_path: str) -> CredentialsScanResult:
        """
        Escaneia um arquivo específico.
        
        Args:
            file_path: Caminho do arquivo para escanear
            
        Returns:
            CredentialsScanResult com os resultados
        """
        logger.info(f"🔍 Escaneando arquivo: {file_path}")
        
        result = CredentialsScanResult(
            scan_path=file_path,
            scan_time=datetime.now(),
            files_scanned=0,
            credentials_found=0
        )
        
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Arquivo não encontrado: {file_path}")
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            result.files_scanned = 1
            
            for line_num, line in enumerate(lines, start=1):
                findings = self._scan_line(line, file_path, line_num)
                result.findings.extend(findings)
            
            result.credentials_found = len(result.findings)
            
            if result.has_credentials:
                self._log_findings(result)
            else:
                logger.info(f"✅ Nenhuma credencial detectada em {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao escanear {file_path}: {e}")
        
        return result
    
    def scan_directory(
        self, 
        directory: str, 
        recursive: bool = True,
        extensions: Optional[set] = None
    ) -> CredentialsScanResult:
        """
        Escaneia todos os arquivos em um diretório.
        
        Args:
            directory: Diretório para escanear
            recursive: Se deve escanear subdiretórios
            extensions: Extensões de arquivo para escanear (None = todas)
            
        Returns:
            CredentialsScanResult agregado
        """
        extensions = extensions or SCANNABLE_EXTENSIONS
        
        logger.info(f"🔍 Escaneando diretório: {directory}")
        
        result = CredentialsScanResult(
            scan_path=directory,
            scan_time=datetime.now(),
            files_scanned=0,
            credentials_found=0
        )
        
        for root, dirs, files in os.walk(directory):
            # Remover diretórios ignorados
            dirs[:] = [d for d in dirs if d not in IGNORED_PATHS]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Verificar se deve escanear este arquivo
                if not self._should_scan_file(file, file_path, extensions):
                    continue
                
                # Escanear arquivo
                file_result = self.scan_file(file_path)
                result.findings.extend(file_result.findings)
                result.files_scanned += 1
        
        result.credentials_found = len(result.findings)
        
        # Log resumo
        logger.info("=" * 60)
        if result.has_credentials:
            logger.critical(f"🚨 ALERTA: {result.credentials_found} credenciais detectadas!")
            self._log_findings(result)
        else:
            logger.info(f"✅ Scan concluído: Nenhuma credencial detectada em {result.files_scanned} arquivos")
        logger.info("=" * 60)
        
        return result
    
    def _should_scan_file(self, filename: str, file_path: str, extensions: set) -> bool:
        """Determina se um arquivo deve ser escaneado."""
        # Ignorar por nome
        if filename in IGNORED_PATHS:
            return False
        
        # Ignorar caminhos completos
        for ignored in IGNORED_PATHS:
            if ignored in file_path:
                return False
        
        # Verificar extensão
        file_ext = os.path.splitext(filename)[1]
        if file_ext in extensions:
            return True
        
        # Arquivos sem extensão como .env
        if filename.startswith('.env') or filename == 'credentials':
            return True
        
        return False
    
    def _scan_line(self, line: str, file_path: str, line_num: int) -> List[CredentialFinding]:
        """Escaneia uma linha em busca de credenciais."""
        findings = []
        
        for cred_type, pattern in self._compiled_patterns.items():
            matches = pattern.finditer(line)
            
            for match in matches:
                # Extrair nome da variável (se disponível)
                variable_name = self._extract_variable_name(line, match, cred_type)
                
                finding = CredentialFinding(
                    file_path=file_path,
                    line_number=line_num,
                    credential_type=cred_type,
                    variable_name=variable_name,
                    severity=self.severity_override.get(cred_type, self._get_default_severity(cred_type))
                )
                findings.append(finding)
        
        return findings
    
    def _extract_variable_name(self, line: str, match: re.Match, cred_type: str) -> str:
        """Extrai o nome da variável da linha."""
        # Tentar encontrar o nome antes do =
        match_eq = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)', line.strip())
        if match_eq:
            return match_eq.group(1)
        
        # Se não encontrar, retornar o tipo
        return cred_type
    
    def _get_default_severity(self, cred_type: str) -> str:
        """Retorna severidade padrão baseada no tipo."""
        high_severity = [
            "RSA_PRIVATE_KEY", "SSH_PRIVATE_KEY", "PGP_PRIVATE_KEY",
            "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
            "JWT_TOKEN", "GITHUB_TOKEN"
        ]
        
        medium_severity = [
            "AWS_ACCESS_KEY_ID", "AZURE_CLIENT_SECRET",
            "API_SECRET", "ACCESS_TOKEN", "REFRESH_TOKEN"
        ]
        
        if cred_type in high_severity:
            return "critical"
        elif cred_type in medium_severity:
            return "high"
        else:
            return "medium"
    
    def _log_findings(self, result: CredentialsScanResult):
        """Gera logs formatados com os achados."""
        logger.critical("=" * 60)
        logger.critical(f"🚨 ALERTA DE SEGURANÇA: {result.credentials_found} credenciais detectadas!")
        logger.critical("=" * 60)
        
        # Agrupar por tipo
        by_type: Dict[str, int] = {}
        for finding in result.findings:
            by_type[finding.credential_type] = by_type.get(finding.credential_type, 0) + 1
        
        for cred_type, count in by_type.items():
            logger.warning(f"   📍 {cred_type}: {count} ocorrência(s)")
        
        # Detalhes dos primeiros 10
        logger.warning("   Detalhes:")
        for i, finding in enumerate(result.findings[:10]):
            logger.warning(
                f"      {i+1}. [{finding.severity.upper()}] "
                f"{finding.credential_type} em {os.path.basename(finding.file_path)}:{finding.line_number}"
            )
        
        if len(result.findings) > 10:
            logger.warning(f"      ... e mais {len(result.findings) - 10} credenciais")
        
        logger.critical("=" * 60)
        logger.critical("⚠️  AÇÃO NECESSÁRIA:")
        logger.critical("   1. Remova credenciais do código/arquivos de configuração")
        logger.critical("   2. Use variáveis de ambiente ou secrets managers")
        logger.critical("   3. Adicione arquivos sensíveis ao .gitignore")
        logger.critical("   4. Rode 'git secrets scan' como verificação adicional")
        logger.critical("=" * 60)


# ============================================
# Funções Helper
# ============================================

def scan_env_files(root_dir: str = ".") -> CredentialsScanResult:
    """
    Escaneia arquivos .env no diretório.
    
    Args:
        root_dir: Diretório raiz para buscar
        
    Returns:
        CredentialsScanResult
    """
    scanner = CredentialsScanner()
    return scanner.scan_directory(
        root_dir, 
        recursive=True,
        extensions={".env", ".env.local", ".env.development", ".env.production"}
    )


def scan_config_files(root_dir: str = ".") -> CredentialsScanResult:
    """
    Escaneia arquivos de configuração no diretório.
    
    Args:
        root_dir: Diretório raiz para buscar
        
    Returns:
        CredentialsScanResult
    """
    scanner = CredentialsScanner()
    return scanner.scan_directory(
        root_dir,
        recursive=True,
        extensions={".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
    )


def check_file_for_secrets(file_path: str) -> bool:
    """
    Verifica se um arquivo contém credenciais.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        True se contém credenciais
    """
    scanner = CredentialsScanner()
    result = scanner.scan_file(file_path)
    return result.has_credentials
