import requests
from typing import Any, Dict
from src.infrastructure.llm.interfaces import LLMProvider
from src.utils.logger import logger

class OllamaProvider(LLMProvider):
    """
    Provedor de LLM para Ollama (Local LLM).
    """

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url
        logger.info(f"OllamaProvider inicializado com modelo: {self.model} em {self.base_url}")

    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            logger.error(f"Erro ao gerar resposta Ollama: {e}")
            raise

    def generate_structured_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Ollama pode retornar JSON se solicitado no prompt e se o modelo for capaz.
        Aqui forçamos o formato via prompt.
        """
        try:
            # Adiciona instrução de formato ao prompt para modelos que não suportam JSON mode nativo
            enhanced_prompt = f"{prompt}\n\nReturn ONLY a valid JSON object."
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{enhanced_prompt}",
                    "stream": False,
                    "format": "json"  # Suporte nativo do Ollama para JSON
                },
                timeout=60
            )
            response.raise_for_status()
            import json
            return json.loads(response.json().get("response", "{}"))
        except Exception as e:
            logger.error(f"Erro ao gerar JSON Ollama: {e}")
            raise
