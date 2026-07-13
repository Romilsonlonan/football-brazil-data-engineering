import os
import json
from typing import Any, Dict, Optional
from openai import OpenAI
from src.infrastructure.llm.interfaces import LLMProvider
from src.utils.logger import logger

class OpenAIProvider(LLMProvider):
    """
    Provedor de LLM para OpenAI.
    """

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None) -> None:
        self.model = model
        # Prioriza a chave passada via argumento, depois via variável de ambiente
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API Key não fornecida. Defina OPENAI_API_KEY no ambiente.")
            
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"OpenAIProvider inicializado com modelo: {self.model}")

    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """Gera uma resposta de texto simples."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2 # Baixa temperatura para maior consistência em tarefas de engenharia
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erro ao gerar resposta OpenAI: {e}")
            raise

    def generate_structured_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Gera uma resposta estruturada em formato JSON usando JSON Mode."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1 # Temperatura mínima para máxima previsibilidade de esquema
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Erro ao gerar JSON OpenAI: {e}")
            raise
