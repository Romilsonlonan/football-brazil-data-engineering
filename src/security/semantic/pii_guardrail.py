from typing import Any, Dict, List, Optional
import pandas as pd
from src.security.semantic.interfaces import SemanticGuardrail, GuardrailResult
from src.infrastructure.llm.service import LLMService
from src.utils.logger import logger

class SemanticPIIGuardrail(SemanticGuardrail):
    """
    Guardrail Semântico para detecção de PII (Personally Identifiable Information) 
    usando análise de contexto via LLM.
    """

    def __init__(self, llm_service: LLMService, sensitivity_threshold: float = 0.7):
        self.llm_service = llm_service
        self.sensitivity_threshold = sensitivity_threshold
        logger.info("🛡️ SemanticPIIGuardrail inicializado com suporte a LLM")

    def evaluate(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa colunas de texto em busca de PII usando LLM.
        """
        columns_to_check = context.get("columns", [])
        findings = []
        
        logger.info(f"🔍 [SemanticPIIGuardrail] Iniciando auditoria semântica via LLM em: {columns_to_check}")

        for col in columns_to_check:
            if col not in df.columns:
                continue
                
            col_findings = self._scan_column_with_llm(df[col], col)
            findings.extend(col_findings)

        is_compliant = len(findings) == 0
        
        result = GuardrailResult(
            is_compliant=is_compliant,
            findings=findings,
            metadata={"columns_scanned": columns_to_check}
        )
        
        return result.to_dict()

    def _scan_column_with_llm(self, series: pd.Series, column_name: str) -> List[Dict[str, Any]]:
        """Utiliza o LLM para analisar o conteúdo de uma coluna."""
        findings = []
        
        # Para não estourar tokens e custos, analisamos uma amostra representativa
        sample_size = min(len(series), 10) 
        sample = series.head(sample_size)

        system_prompt = (
            "Você é um especialista em privacidade de dados e proteção de PII. "
            "Sua tarefa é analisar textos e identificar se eles contêm informações sensíveis "
            "(CPF, nomes, endereços, telefones, etc). "
            "Responda estritamente em formato JSON conforme o esquema abaixo:\n"
            "{\n"
            "  \"is_pii\": boolean,\n"
            "  \"reason\": \"breve explicação\",\n"
            "  \"confidence\": float (0 a 1)\n"
            "}"
        )

        for idx, value in sample.items():
            text = str(value)
            if len(text) < 5:
                continue

            prompt = f"Analise o seguinte texto e identifique se há PII: '{text}'"
            
            try:
                # Chamada ao LLM para obter resposta estruturada
                response = self.llm_service.ask_json(prompt, system_prompt=system_prompt)
                
                if response.get("is_pii") and response.get("confidence", 0) >= self.sensitivity_threshold:
                    findings.append({
                        "column": column_name,
                        "row": idx,
                        "issue": response.get("reason", "PII detectado"),
                        "severity": "high",
                        "evidence": text[:30] + "..."
                    })
            except Exception as e:
                logger.error(f"Erro na análise semântica da linha {idx} na coluna {column_name}: {e}")

        return findings
