import os
import pytest
from src.infrastructure.llm.openai_provider import OpenAIProvider
from src.infrastructure.llm.service import LLMService

def test_openai_integration():
    """
    Teste de integração real com OpenAI.
    Este teste deve ser pulado se a API Key não estiver configurada.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        pytest.skip("Pulando teste de integração OpenAI: OPENAI_API_KEY não configurada.")

    provider = OpenAIProvider(api_key=api_key)
    service = LLMService(provider)
    
    # Teste de texto simples
    response = service.ask("Diga apenas a palavra 'Teste'.", system_prompt="Você é um assistente conciso.")
    assert "Teste" in response
    
    # Teste de JSON estruturado
    json_response = service.ask_json(
        "Responda com um JSON contendo a chave 'status' como 'ok'", 
        system_prompt="Você é um assistente que responde apenas em JSON."
    )
    assert json_response["status"] == "ok"
    
    print("\n✅ Teste de Integração OpenAI (Real) passou!")

if __name__ == "__main__":
    # Executa manualmente se o script for chamado diretamente
    try:
        test_openai_integration()
    except Exception as e:
        print(f"Erro ao executar teste: {e}")
