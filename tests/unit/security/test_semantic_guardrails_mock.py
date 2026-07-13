import pandas as pd
import pytest
from src.infrastructure.llm.mock_provider import MockLLMProvider
from src.infrastructure.llm.service import LLMService
from src.security.semantic.pii_guardrail import SemanticPIIGuardrail
from src.security.semantic.quality_guardrail import SemanticQualityGuardrail

@pytest.fixture
def llm_service():
    provider = MockLLMProvider()
    return LLMService(provider)

def test_pii_guardrail_mock(llm_service):
    guardrail = SemanticPIIGuardrail(llm_service)
    df = pd.DataFrame({
        "name": ["John Doe", "Jane Doe"],
        "cpf": ["00000000000", "99999999999"]
    })
    
    context = {"columns": ["cpf"]}
    result = guardrail.evaluate(df, context)
    
    assert result["is_compliant"] is False
    assert len(result["findings"]) > 0
    assert result["findings"][0]["issue"] == "Detectado padrão de CPF"

def test_quality_guardrail_mock_plausible(llm_service):
    guardrail = SemanticQualityGuardrail(llm_service)
    df = pd.DataFrame({
        "player_name": ["Neymar", "Messi"],
        "goals": [100, 200]
    })
    
    rules = [{
        "column": "player_name",
        "type": "semantic_plausibility",
        "params": {"description": "jogador de futebol"}
    }]
    
    context = {"rules": rules}
    result = guardrail.evaluate(df, context)
    
    assert result["is_compliant"] is True

def test_quality_guardrail_mock_implausible(llm_service):
    guardrail = SemanticQualityGuardrail(llm_service)
    df = pd.DataFrame({
        "player_name": ["Neymar", "Messi"],
        "goals": [100, 200]
    })
    
    # By using "impossível" in the description, the prompt will contain it, 
    # and the MockLLMProvider will return is_plausible: False.
    rules = [{
        "column": "player_name",
        "type": "semantic_plausibility",
        "params": {"description": "algo impossível"}
    }]
    
    context = {"rules": rules}
    result = guardrail.evaluate(df, context)
    
    assert result["is_compliant"] is False
    assert len(result["findings"]) > 0
    assert result["findings"][0]["issue"] == "Valor totalmente fora do esperado para futebol"
