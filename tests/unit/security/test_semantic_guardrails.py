import pandas as pd
from src.security.semantic.pii_guardrail import SemanticPIIGuardrail
from src.security.semantic.quality_guardrail import SemanticQualityGuardrail
from src.infrastructure.llm.mock_provider import MockLLMProvider
from src.infrastructure.llm.service import LLMService

# Caminhos para dados reais no projeto
DATA_DIR = "data"

class RealDataTest:
    @staticmethod
    def get_elenco_df():
        # Carrega o elenco real da camada bronze
        return pd.read_parquet(f"{DATA_DIR}/bronze/elenco.parquet")

    @staticmethod
    def get_classificacao_df():
        # Carrega a classificação real da camada bronze
        return pd.read_parquet(f"{DATA_DIR}/bronze/classificacao.parquet")

def test_semantic_pii_guardrail_with_real_data():
    llm_service = LLMService(MockLLMProvider())
    guardrail = SemanticPIIGuardrail(llm_service)
    
    # Usando dados reais de elenco
    df = RealDataTest.get_elenco_df()
    
    # Testamos em colunas que teoricamente podem ter PII (ex: nomes)
    # Nota: Como estamos com MockLLM, ele ainda não "entenderá" o texto, 
    # mas validamos o fluxo de dados real.
    # Procuramos a coluna correta (o arquivo tem 'Nome' ou 'nome')
    col_name = "Nome" if "Nome" in df.columns else "nome"
    
    result = guardrail.evaluate(df, {"columns": [col_name]})
    
    assert "is_compliant" in result
    print("\n✅ Teste de PII Guardrail (Dados Reais) executado!")

def test_semantic_quality_guardrail_with_real_data():
    llm_service = LLMService(MockLLMProvider())
    guardrail = SemanticQualityGuardrail(llm_service)
    
    # Usando dados reais de classificação
    df = RealDataTest.get_classificacao_df()
    
    # Definindo regras baseadas no schema real (ex: pontos não podem ser negativos)
    # Vamos tentar encontrar uma coluna numérica para o teste de range
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        rules = [
            {"column": numeric_cols[0], "type": "range", "params": {"min": 0, "max": 1000}},
        ]
        result = guardrail.evaluate(df, {"rules": rules})
        assert "is_compliant" in result
        print(f"\n✅ Teste de Quality Guardrail (Dados Reais) executado na coluna '{numeric_cols[0]}'!")
    else:
        print(f"\n⚠️ Nenhuma coluna numérica encontrada nos dados reais para teste de qualidade.")

if __name__ == "__main__":
    test_semantic_pii_guardrail_with_real_data()
    test_semantic_quality_guardrail_with_real_data()
