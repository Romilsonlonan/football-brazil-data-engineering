#!/usr/bin/env python3
# ============================================
# Script de Pre-Commit - Verifica dados sensíveis
# ============================================
# Uso: python3 scripts/pre-commit-check.py
#
# Para usar automaticamente antes de commits:
# cp scripts/pre-commit-check.py .git/hooks/pre-commit
# chmod +x .git/hooks/pre-commit
# ============================================

import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


# Cores para terminal
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


# ============================================
# MÓDULO DE LOGGING DE SEGURANÇA
# ============================================
class SecurityLogger:
    """Logger de segurança para o pré-commit."""

    def __init__(self, log_file: str = "logs/security-pre-commit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.findings: List[Dict[str, Any]] = []

    def _log(self, level: str, message: str, details: str = ""):
        """Escreve log no arquivo e stdout."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        if details:
            log_entry += f"\n{details}"

        # Escreve no arquivo
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def info(self, message: str):
        print(f"{Colors.CYAN}ℹ️  {message}{Colors.NC}")
        self._log("INFO", message)

    def warning(self, message: str, details: str = ""):
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
        if details:
            print(f"   {details}")
        self._log("WARNING", message, details)

    def error(self, message: str, details: str = ""):
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
        if details:
            print(f"   {details}")
        self._log("ERROR", message, details)

    def success(self, message: str):
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
        self._log("SUCCESS", message)

    def critical(self, message: str, details: str = ""):
        print(f"{Colors.RED}{Colors.BOLD}🔴 {message}{Colors.NC}")
        if details:
            print(f"   {details}")
        self._log("CRITICAL", message, details)

    def add_finding(self, finding: Dict[str, Any]):
        """Adiciona uma descoberta para relatório final."""
        self.findings.append(finding)

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos achados."""
        return {
            "total": len(self.findings),
            "by_severity": self._count_by_severity(),
            "by_type": self._count_by_type(),
        }

    def _count_by_severity(self) -> Dict[str, int]:
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for f in self.findings:
            sev = f.get("severity", "low")
            if sev in counts:
                counts[sev] += 1
        return counts

    def _count_by_type(self) -> Dict[str, int]:
        counts = {}
        for f in self.findings:
            t = f.get("type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts


# ============================================
# SCANNERS DE SEGURANÇA
# ============================================
class SecretPatternsScanner:
    """Scanner de padrões sensíveis (regex)."""

    # Emails permitidos (não são credenciais reais)
    EMAIL_ALLOWLIST = [
        "admin@superset.com",  # Email padrão do usuário admin do Superset
        "admin@lakehouse.com",  # Email do administrador do projeto
    ]

    # Arquivos a ignorar completamente
    IGNORE_FILES = [
        "docker-compose.yaml",
        ".env",
    ]

    # Padrões de dados sensíveis
    PATTERNS = {
        "cpf": {
            "pattern": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",
            "severity": "critical",
            "description": "CPF exposto",
        },
        "email": {
            "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "severity": "critical",
            "description": "Endereço de email exposto",
        },
        "password": {
            "pattern": r'password\s*[=:]\s*["\'](?!{{|\$\{|<%|%>)[^"\']{3,}["\']',
            "severity": "critical",
            "description": "Senha exposta",
        },
        "secret_key": {
            "pattern": r'secret[_-]?key\s*[=:]\s*["\'][^"\']{8,}["\']',
            "severity": "critical",
            "description": "Chave secreta exposta",
        },
        "api_key": {
            "pattern": r'api[_-]?key\s*[=:]\s*["\'][^"\']{8,}["\']',
            "severity": "high",
            "description": "API Key exposta",
        },
        "token": {
            "pattern": r'(access[_-]?token|auth[_-]?token|session[_-]?token)\s*[=:]\s*["\'][^"\']{8,}["\']',
            "severity": "high",
            "description": "Token de acesso exposto",
        },
        "aws_access_key": {
            "pattern": r"AKIA[0-9A-Z]{16}",
            "severity": "critical",
            "description": "AWS Access Key ID",
        },
        "aws_secret_key": {
            "pattern": r'aws[_-]?secret[_-]?key\s*[=:]\s*["\'][A-Za-z0-9/+=]{40}["\']',
            "severity": "critical",
            "description": "AWS Secret Key",
        },
        "private_key": {
            "pattern": r"-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PRIVATE)\s+KEY-----",
            "severity": "critical",
            "description": "Chave privada",
        },
        "jwt_token": {
            "pattern": r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+",
            "severity": "high",
            "description": "JWT Token",
        },
        "connection_string": {
            "pattern": r"(mongodb|postgres|mysql|redis)://[^@]+:[^@]+@",
            "severity": "critical",
            "description": "String de conexão com credenciais",
        },
        " Bearer ": {
            "pattern": r"Bearer\s+[A-Za-z0-9\-_.~+/]+=*",
            "severity": "high",
            "description": "Authorization Bearer Token",
        },
    }

    def __init__(self, logger: SecurityLogger):
        self.logger = logger

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Escaneia um arquivo em busca de padrões sensíveis."""
        findings = []

        # Ignora arquivos específicos
        if str(file_path) in self.IGNORE_FILES:
            return findings

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for name, config in self.PATTERNS.items():
                    match = re.search(config["pattern"], line, re.IGNORECASE)
                    if match:
                        # Verificar se é email permitido
                        if name == "email":
                            email_found = match.group(0)
                            if email_found in self.EMAIL_ALLOWLIST:
                                continue  # Ignorar email permitido

                        finding = {
                            "type": name,
                            "severity": config["severity"],
                            "description": config["description"],
                            "file": str(file_path),
                            "line": line_num,
                            "snippet": line.strip()[:80],
                        }
                        findings.append(finding)
                        self.logger.add_finding(finding)

        except Exception as e:
            self.logger.warning(f"Erro ao escanear {file_path}: {e}")

        return findings


class CredentialsScanner:
    """Wrapper para o CredentialsScanner do projeto."""

    # Arquivos e pastas a ignorar (falsos positivos conhecidos)
    IGNORE_PATTERNS = [
        "src/security/",  # scanner de credenciais detecta seus próprios padrões
        "src/api/infrastructure/database/connection.py",  # usa variáveis de ambiente
        "src/pipelines/gold/carga_classificacao.py",  # usa configurações do settings
        "k8s/",  # templates K8s usam placeholders
        "docker-compose.yaml",  # usa variáveis de ambiente com placeholders
        ".env.example",  # arquivo de exemplo com placeholders
    ]

    def __init__(self, logger: SecurityLogger):
        self.logger = logger
        self.scanner = None
        self._load_scanner()

    def _load_scanner(self):
        """Carrega o scanner de credenciais do projeto."""
        try:
            sys.path.insert(0, ".")
            from src.security.credentials_scanner import (
                CredentialsScanner as ProjectScanner,
            )

            self.scanner = ProjectScanner()
            self.logger.info("CredentialsScanner do projeto carregado com sucesso")
        except ImportError as e:
            self.logger.warning(f"CredentialsScanner não disponível: {e}")

    def _should_ignore(self, file_path: str) -> bool:
        """Verifica se o arquivo deve ser ignorado."""
        for pattern in self.IGNORE_PATTERNS:
            if pattern in file_path:
                return True
        return False

    def scan_files(self, files: List[str]) -> List[Dict[str, Any]]:
        """Escaneia arquivos específicos em busca de credenciais."""
        if not self.scanner:
            return []

        findings = []
        try:
            for file_path in files:
                # Ignora arquivos que devem ser pulados
                if self._should_ignore(file_path):
                    continue

                result = self.scanner.scan_file(file_path)

                if result.has_credentials:
                    for finding in result.findings:
                        findings.append(
                            {
                                "type": finding.credential_type,
                                "severity": "high",
                                "description": f"Credencial: {finding.credential_type}",
                                "file": finding.file_path,
                                "line": finding.line_number,
                                "variable": finding.variable_name,
                            }
                        )
                        self.logger.add_finding(findings[-1])

        except Exception as e:
            self.logger.warning(f"Erro ao usar CredentialsScanner: {e}")

        return findings


class EnvFileScanner:
    """Scanner específico para arquivos .env."""

    def __init__(self, logger: SecurityLogger):
        self.logger = logger
        self.exposed_vars = []

    def scan_env_files(self, root_dir: str = ".") -> List[Dict[str, Any]]:
        """Verifica arquivos .env para variáveis sensíveis expostas."""
        findings = []

        # Variáveis que NÃO devem estar em .env.example
        sensitive_vars = [
            "PASSWORD",
            "SECRET",
            "KEY",
            "TOKEN",
            "PRIVATE",
            "AWS_ACCESS",
            "AWS_SECRET",
            "API_KEY",
            "CREDENTIAL",
        ]

        env_files = list(Path(root_dir).glob("**/.env*"))

        for env_file in env_files:
            # Ignora .env.local, .env de desenvolvimento e .env principal
            if (
                ".env.local" in str(env_file)
                or ".env.dev" in str(env_file)
                or str(env_file) == ".env"
            ):
                continue

            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            var_name = line.split("=")[0].strip()

                            # Verifica se variável sensível tem valor real (não placeholder)
                            if any(sv in var_name.upper() for sv in sensitive_vars):
                                value = line.split("=", 1)[1].strip()
                                if value and not any(
                                    ph in value
                                    for ph in ["changeme", "your-", "example", "<", ">"]
                                ):
                                    finding = {
                                        "type": "env_sensitive_value",
                                        "severity": "medium",
                                        "description": f"Variável sensível com valor real: {var_name}",
                                        "file": str(env_file),
                                        "line": line_num,
                                        "variable": var_name,
                                    }
                                    findings.append(finding)
                                    self.logger.add_finding(finding)

            except Exception as e:
                self.logger.warning(f"Erro ao escanear {env_file}: {e}")

        return findings


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def main():
    """Função principal do script de pré-commit."""
    logger = SecurityLogger()

    print(f"\n{Colors.BOLD}{'='*60}")
    print("🔒 VERIFICAÇÃO DE SEGURANÇA - PRÉ-COMMIT")
    print(f"{'='*60}{Colors.NC}\n")

    # Se estiver em modo CI, verifica todos os arquivos relevantes
    ci_mode = "--ci-mode" in sys.argv
    if ci_mode:
        logger.info("Modo CI detectado - Verificando todos os arquivos relevantes")
        # Lista recursivamente todos os arquivos, ignorando .git e logs
        all_files = [
            str(p)
            for p in Path(".").rglob("*")
            if p.is_file()
            and not any(part.startswith(".") for part in p.parts)
            and "logs" not in str(p)
        ]
    else:
        # Verifica se está em repositório git
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"], check=True, capture_output=True
            )
        except subprocess.CalledProcessError:
            logger.error("Não está em um repositório git")
            sys.exit(1)

        # Obtém arquivos modificados
        try:
            staged = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
            ).stdout.strip()

            modified = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACM"],
                capture_output=True,
                text=True,
            ).stdout.strip()

            all_files = list(
                set(
                    f
                    for f in (staged + "\n" + modified).split("\n")
                    if f and Path(f).exists()
                )
            )

            # Filtrar arquivos ignorados pelo .gitignore
            try:
                git_ignore = (
                    subprocess.run(
                        ["git", "check-ignore", "--no-index"] + all_files,
                        capture_output=True,
                        text=True,
                    )
                    .stdout.strip()
                    .split("\n")
                )
                ignored_files = set(f for f in git_ignore if f)
                all_files = [f for f in all_files if f not in ignored_files]
                if ignored_files:
                    logger.info(
                        f"Arquivos ignorados pelo .gitignore: {len(ignored_files)}"
                    )
            except Exception:
                pass  # Se falhar, continua com todos os arquivos
        except Exception as e:
            logger.error(f"Erro ao obter arquivos: {e}")
            sys.exit(1)

    if not all_files:
        logger.success("Nenhum arquivo modificado para verificar")
        sys.exit(0)

    logger.info(f"Arquivos a verificar: {len(all_files)}")
    for f in all_files[:10]:
        logger.info(f"  - {f}")
    if len(all_files) > 10:
        logger.info(f"  ... e mais {len(all_files) - 10} arquivos")

    # Escaneia arquivos
    logger.info("\n" + "=" * 40)
    logger.info("🔍 ESCANEANDO ARQUIVOS...")
    logger.info("=" * 40 + "\n")

    # 1. Scanner de padrões secretos
    secret_scanner = SecretPatternsScanner(logger)
    for file_path in all_files:
        if not Path(file_path).is_file():
            continue
        # Pula binários
        if any(
            file_path.endswith(ext) for ext in [".png", ".jpg", ".pdf", ".exe", ".so"]
        ):
            continue
        # Pula arquivos de exemplo
        if file_path.endswith(".env.example"):
            continue
        secret_scanner.scan_file(Path(file_path))

    # 2. Scanner de credenciais do projeto
    cred_scanner = CredentialsScanner(logger)
    cred_scanner.scan_files(all_files)

    # 3. Scanner de arquivos .env
    env_scanner = EnvFileScanner(logger)
    env_scanner.scan_env_files()

    # Resultado
    logger.info("\n" + "=" * 40)
    logger.info("📊 RESUMO DA VERIFICAÇÃO")
    logger.info("=" * 40 + "\n")

    summary = logger.get_summary()
    logger.info(f"Total de achados: {summary['total']}")

    if summary["by_severity"]:
        logger.info("\nPor severidade:")
        for sev, count in summary["by_severity"].items():
            if count > 0:
                emoji = (
                    "🔴"
                    if sev == "critical"
                    else "🟠"
                    if sev == "high"
                    else "🟡"
                    if sev == "medium"
                    else "🔵"
                )
                logger.info(f"  {emoji} {sev.upper()}: {count}")

    if summary["by_type"]:
        logger.info("\nPor tipo:")
        for type_name, count in summary["by_type"].items():
            logger.info(f"  - {type_name}: {count}")

    # Decisão final
    print(f"\n{Colors.BOLD}{'='*60}{Colors.NC}")

    critical_count = summary["by_severity"].get("critical", 0)
    high_count = summary["by_severity"].get("high", 0)

    if critical_count > 0:
        logger.critical(
            f"❌ COMMIT BLOQUEADO: {critical_count} problema(s) crítico(s) encontrado(s)",
            "\n".join(
                [
                    f"  - {f['file']}:{f['line']} ({f['type']})"
                    for f in logger.findings[:10]
                ]
            ),
        )
        print(
            f"\n{Colors.YELLOW}Para forçar o commit use: git commit --no-verify{Colors.NC}"
        )
        sys.exit(1)
    elif high_count > 0:
        logger.warning(
            f"⚠️  ATENÇÃO: {high_count} problema(s) de alta severidade",
            "\n".join([f"  - {f['file']}:{f['line']}" for f in logger.findings[:5]]),
        )
        print(f"\n{Colors.YELLOW}Revise os achados antes de continuar.{Colors.NC}")
        print(
            f"{Colors.YELLOW}Para forçar o commit use: git commit --no-verify{Colors.NC}"
        )
        sys.exit(1)
    else:
        logger.success("✅ Nenhum problema crítico encontrado!")
        logger.info("Pronto para commit.")
        sys.exit(0)


if __name__ == "__main__":
    main()
