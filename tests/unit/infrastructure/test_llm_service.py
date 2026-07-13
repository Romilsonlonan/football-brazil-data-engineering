from src.infrastructure.llm.mock_provider import MockLLMProvider
from src.infrastructure.llm.service import LLMService

def test_llm_service_with_mock():
    provider = MockLLMProvider()
    service = LLMService(provider)
    
    # Teste de texto simples
    response = service.ask("Is there PII here?")
    assert "Sim" in response or "Não" in response or "Resposta" in response
    
    # Teste de JSON estruturado
    json_response = service.ask_json("Analyze this for PII", system_prompt="You are a security expert")
    assert "is_pii" in json_response
    assert isinstance(json_response["is_pii"], bool)
    
    print("\n✅ Teste de LLMService com Mock passou!")

if __name__ == "__main__":
    test_llm_service_with_mock()
