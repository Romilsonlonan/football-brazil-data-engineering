from typing import Any, Dict
from src.infrastructure.llm.interfaces import LLMProvider
from src.utils.logger import logger
import json

class MockLLMProvider(LLMProvider):
    """
    Provedor de LLM para testes e desenvolvimento sem custos de API.
    Simula respostas baseadas em palavras-chave.
    """

    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        logger.info("[MockLLMProvider] Gerando resposta simulada...")
        prompt_lower = prompt.lower()
        
        if "pii" in prompt_lower or "sensitive" in prompt_lower:
            return "Sim, este texto contém dados sensíveis como um CPF."
        
        if "plausibility" in prompt_lower or "quality" in prompt_lower or "plausível" in prompt_lower:
            if "não é plausível" in prompt_lower or "impossível" in prompt_lower:
                 return "O valor é impossível no contexto de futebol."
            return "O valor parece plausível dentro do contexto de futebol."
        
        return "Resposta simulada padrão."


    def generate_structured_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        logger.info("[MockLLMProvider] Gerando JSON simulado...")
        prompt_lower = prompt.lower()
        
        if "pii" in prompt_lower:
            return {
                "is_pii": True,
                "reason": "Detectado padrão de CPF",
                "confidence": 0.95
            }
        
        if "plausibility" in prompt_lower or "quality" in prompt_lower or "plausível" in prompt_lower:
            if "impossível" in prompt_lower:
                return {
                    "is_plausible": False,
                    "reason": "Valor totalmente fora do esperado para futebol",
                    "confidence": 0.9
                }
            return {
                "is_plausible": True,
                "reason": "Dados condizentes com o domínio",
                "confidence": 0.9
            }
        
        return {"status": "ok", "message": "Mock response"}

