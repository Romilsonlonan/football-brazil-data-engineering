from abc import ABC, abstractmethod
from typing import Any, Dict

class LLMProvider(ABC):
    """
    Interface para provedores de LLM (OpenAI, Anthropic, Ollama, etc).
    """

    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """
        Gera uma resposta baseada em um prompt.

        Args:
            prompt: O prompt do usuário.
            system_prompt: Instruções de sistema para o modelo.

        Returns:
            A string com a resposta gerada pelo modelo.
        """
        pass

    @abstractmethod
    def generate_structured_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Gera uma resposta estruturada em formato JSON.

        Args:
            prompt: O prompt do usuário.
            system_prompt: Instruções de sistema para o modelo.

        Returns:
            Um dicionário contendo a resposta estruturada.
        """
        pass
