from typing import Any, Dict, Optional
from src.infrastructure.llm.interfaces import LLMProvider
from src.infrastructure.llm.mock_provider import MockLLMProvider
from src.infrastructure.llm.openai_provider import OpenAIProvider
from src.infrastructure.llm.ollama_provider import OllamaProvider
from src.utils.logger import logger

class LLMFactory:
    """
    Factory para instanciar o provedor de LLM correto.
    """

    @staticmethod
    def get_provider(provider_type: str, **kwargs) -> LLMProvider:
        provider_type = provider_type.lower()
        
        if provider_type == "mock":
            return MockLLMProvider()
        elif provider_type == "openai":
            return OpenAIProvider(**kwargs)
        elif provider_type == "ollama":
            return OllamaProvider(**kwargs)
        else:
            raise ValueError(f"Provedor desconhecido: {provider_type}")

class LLMService:
    """
    Serviço central para interação com modelos de linguagem.
    """

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider
        logger.info(f"LLMService inicializado com provedor: {provider.__class__.__name__}")

    def ask(self, prompt: str, system_prompt: str = "") -> str:
        """Pergunta algo ao modelo (texto simples)."""
        return self._provider.generate_response(prompt, system_prompt)

    def ask_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Pergunta algo ao modelo e espera um retorno estruturado (JSON)."""
        return self._provider.generate_structured_json(prompt, system_prompt)
