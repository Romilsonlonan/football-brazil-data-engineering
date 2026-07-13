from typing import Any, Dict, Optional
import pandas as pd
import re
from src.pipelines.recovery.interfaces import RecoveryAgent, RecoveryResult
from src.utils.logger import logger

class SchemaRecoveryAgent(RecoveryAgent):
    """
    Agente especializado em recuperar pipelines quando ocorrem erros de schema (colunas ausentes ou renomeadas).
    """

    def attempt_recovery(self, exception: Exception, context: Dict[str, Any]) -> Optional[RecoveryResult]:
        step = context.get("step")
        df = context.get("data")
        error_msg = str(exception).lower()

        # Só faz sentido tentar recuperar se o erro for durante transform ou load
        if step not in ["transform", "load"] or df is None:
            return None

        logger.info(f"🔍 [SchemaRecoveryAgent] Analisando erro no passo '{step}'...")

        # Tentativa de detectar erro de coluna ausente via padrões comuns do Pandas
        if any(pattern in error_msg for pattern in ["not in index", "keyerror", "column", "key", "not found"]):
            return self._handle_missing_column(str(exception), df)

        return None

    def _handle_missing_column(self, error_msg: str, df: pd.DataFrame) -> Optional[RecoveryResult]:
        """Tenta identificar qual coluna falta e cria uma coluna vazia para permitir a continuidade."""
        
        # Tentativa 1: Procurar por conteúdo entre aspas simples (comum no Pandas KeyError)
        # Ex: "['col_missing'] not in index" ou "'col_missing'"
        match = re.search(r"'([^']+)'", error_msg)
        
        # Tentativa 2: Se não funcionar, procurar por conteúdo entre aspas duplas
        if not match:
            match = re.search(r"\"([^\"]+)\"", error_msg)
            
        # Tentativa 3: Se ainda não funcionar, tentar algo mais genérico para pegar o que está dentro de []
        if not match:
            match = re.search(r"\[['\"]?([^'\"\]]+)['\"]?\]", error_msg)

        if match:
            missing_col = match.group(1).strip()
            
            # Evitar falsos positivos como '[' ou ']'
            if missing_col in ["[", "]", "'", '"']:
                return None

            logger.warning(f"⚠️ [SchemaRecoveryAgent] Detectada coluna ausente: '{missing_col}'")
            
            # Estratégia de recuperação: Adiciona a coluna com valores nulos para permitir a continuidade
            df[missing_col] = None
            
            return RecoveryResult(
                success=True,
                corrected_data=df,
                message=f"Coluna '{missing_col}' adicionada como vazia para permitir continuidade."
            )

        return None
