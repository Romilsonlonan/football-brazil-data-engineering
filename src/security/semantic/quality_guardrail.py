from typing import Any, Dict, List, Optional
import pandas as pd
from src.security.semantic.interfaces import SemanticGuardrail, GuardrailResult
from src.infrastructure.llm.service import LLMService
from src.utils.logger import logger

class SemanticQualityGuardrail(SemanticGuardrail):
    """
    Guardrail Semântico para auditoria de plausibilidade de dados usando LLM.
    Verifica se os valores fazem sentido dentro do contexto do domínio.
    """

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        logger.info("🛡️ SemanticQualityGuardrail inicializado com suporte a LLM")

    def evaluate(self, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audita a plausibilidade dos dados usando LLM para julgamentos complexos.
        """
        rules = context.get("rules", [])
        findings = []
        
        logger.info(f"🔍 [SemanticQualityGuardrail] Iniciando auditoria de qualidade via LLM em {len(rules)} regras.")

        for rule in rules:
            column = rule.get("column")
            rule_type = rule.get("type")
            params = rule.get("params", {})

            if column not in df.columns:
                continue

            # Regras estruturadas (rápidas)
            if rule_type == "range":
                findings.extend(self._check_range(df, column, params))
            elif rule_type == "set":
                findings.extend(self._check_set(df, column, params))
            
            # Regras semânticas (lentas/LLM)
            elif rule_type == "semantic_plausibility":
                findings.extend(self._check_semantic_plausibility(df, column, params))

        is_compliant = len(findings) == 0
        
        result = GuardrailResult(
            is_compliant=is_compliant,
            findings=findings,
            metadata={"rules_applied": len(rules)}
        )
        
        return result.to_dict()

    def _check_range(self, df: pd.DataFrame, column: str, params: Dict) -> List[Dict]:
        findings = []
        min_val = params.get("min")
        max_val = params.get("max")
        
        if min_val is not None and max_val is not None:
            outliers = df[(df[column] < min_val) | (df[column] > max_val)]
            for idx, row in outliers.iterrows():
                findings.append({
                    "column": column,
                    "row": idx,
                    "issue": f"Value {row[column]} out of range [{min_val}, {max_val}]",
                    "severity": "medium"
                })
        return findings

    def _check_set(self, df: pd.DataFrame, column: str, params: Dict) -> List[Dict]:
        findings = []
        allowed_set = params.get("allowed", [])
        
        if allowed_set:
            invalid_mask = ~df[column].astype(str).isin([str(x) for x in allowed_set])
            invalid_rows = df[invalid_mask]
            
            for idx, row in invalid_rows.iterrows():
                findings.append({
                    "column": column,
                    "row": idx,
                    "issue": f"Value '{row[column]}' not in allowed set",
                    "severity": "low"
                })
        return findings

    def _check_semantic_plausibility(self, df: pd.DataFrame, column: str, params: Dict) -> List[Dict]:
        """Usa o LLM para verificar se um valor é plausível para o domínio."""
        findings = []
        description = params.get("description", "valor do domínio")
        
        sample_size = min(len(df), 5)
        sample = df[column].head(sample_size)

        system_prompt = (
            "Você é um auditor de dados de futebol. Sua tarefa é verificar se um valor é plausível "
            "dentro do contexto fornecido. Responda estritamente em formato JSON:\n"
            "{\n"
            "  \"is_plausible\": boolean,\n"
            "  \"reason\": \"explicação curta\",\n"
            "  \"confidence\": float (0 a 1)\n"
            "}"
        )

        for idx, value in sample.items():
            prompt = f"O valor '{value}' é plausível para um(a) {description} no contexto de futebol? Responda apenas JSON."
            
            try:
                response = self.llm_service.ask_json(prompt, system_prompt=system_prompt)
                
                if not response.get("is_plausible") and response.get("confidence", 0) > 0.7:
                    findings.append({
                        "column": column,
                        "row": idx,
                        "issue": response.get("reason", "Valor implausível"),
                        "severity": "medium"
                    })
            except Exception as e:
                logger.error(f"Erro na auditoria semântica da linha {idx} na coluna {column}: {e}")

        return findings
