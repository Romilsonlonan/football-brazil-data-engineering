from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd

class SemanticGuardrail(ABC):
    """
    Interface para Guardrails Semânticos.
    Diferente dos agentes de recuperação, o objetivo aqui é auditar a qualidade
    e a conformidade semântica dos dados.
    """

    @abstractmethod
    def evaluate(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Avalia o DataFrame sob uma perspectiva semântica.

        Args:
            df: O DataFrame a ser auditado.
            context: Contexto da auditoria (ex: 'table_name', 'column_to_check', 'rules').

        Returns:
            Um dicionário contendo o resultado da auditoria.
            Exemplo de retorno:
            {
                "is_compliant": False,
                "findings": [
                    {"column": "desc", "issue": "PII detected", "severity": "high", "row": 10}
                ],
                "metadata": {...}
            }
        """
        pass

class GuardrailResult:
    """Representa o resultado de uma auditoria semântica."""
    def __init__(self, is_compliant: bool, findings: list = None, metadata: dict = None):
        self.is_compliant = is_compliant
        self.findings = findings or []
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "is_compliant": self.is_compliant,
            "findings": self.findings,
            "metadata": self.metadata
        }
