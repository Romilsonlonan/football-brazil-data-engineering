from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class RecoveryAgent(ABC):
    """
    Interface para agentes de recuperação de erros em pipelines.
    """

    @abstractmethod
    def attempt_recovery(self, exception: Exception, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analisa uma exceção e tenta propor uma correção.

        Args:
            exception: A exceção capturada.
            context: Dicionário contendo informações do contexto (ex: 'df', 'pipeline_name', 'step').

        Returns:
            Um dicionário contendo os dados ou parâmetros corrigidos, ou None se a recuperação falhar.
        """
        pass

class RecoveryResult:
    """
    Representa o resultado de uma tentativa de recuperação.
    """
    def __init__(self, success: bool, corrected_data: Optional[Any] = None, message: str = ""):
        self.success = success
        self.corrected_data = corrected_data
        self.message = message
