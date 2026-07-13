from typing import Any, Dict, Optional
import pandas as pd
import re
from src.pipelines.recovery.interfaces import RecoveryAgent, RecoveryResult
from src.utils.logger import logger

class DataTypeRecoveryAgent(RecoveryAgent):
    """
    Agente especializado em recuperar pipelines quando ocorrem erros de conversão de tipos de dados.
    Ex: Tentar converter uma coluna de string para float e encontrar valores como 'N/A'.
    """

    def attempt_recovery(self, exception: Exception, context: Dict[str, Any]) -> Optional[RecoveryResult]:
        step = context.get("step")
        df = context.get("data")
        
        # Mantemos a mensagem original para preservar o casing (maiúsculas/minúsculas) para o regex
        error_msg = str(exception)

        # Só faz sentido tentar recuperar se o erro for durante transform ou load
        if step not in ["transform", "load"] or df is None:
            return None

        logger.info(f"🔍 [DataTypeRecoveryAgent] Analisando erro no passo '{step}'...")

        # Detectar erros comuns de conversão de tipos (ValueError, TypeError)
        if isinstance(exception, (ValueError, TypeError)):
            return self._handle_type_error(error_msg, df)

        return None

    def _handle_type_error(self, error_msg: str, df: pd.DataFrame) -> Optional[RecoveryResult]:
        """
        Tenta identificar a coluna problemática através da mensagem de erro e limpa a coluna.
        """
        
        # Tentativa 1: Tentar extrair o nome da coluna diretamente da mensagem de erro
        column_match = re.search(r"column\s+['\"]([^'\"]+)['\"]", error_msg, re.IGNORECASE)
        if column_match:
            column_name = column_match.group(1)
            if column_name in df.columns:
                logger.warning(f"⚠️ [DataTypeRecoveryAgent] Coluna identificada via erro: '{column_name}'")
                return self._apply_cleaning(df, column_name)
        
        # Tentativa 2: Se não achou a coluna, tentar achar o valor problemático e procurar a coluna (fallback)
        value_match = re.search(r"['\"]([^'\"]+)['\"]", error_msg)
        if value_match:
            problematic_value = value_match.group(1)
            
            # Evitar falsos positivos de palavras comuns em mensagens de erro
            if problematic_value.lower() not in ["column", "index", "key", "error", "float", "int", "string"]:
                for col in df.columns:
                    # Busca case-insensitive no dataframe
                    if df[col].astype(str).str.contains(re.escape(problematic_value), case=False, na=False).any():
                        logger.warning(f"⚠️ [DataTypeRecoveryAgent] Valor '{problematic_value}' detectado na coluna '{col}'")
                        return self._apply_cleaning(df, col, problematic_value)

        return None

    def _apply_cleaning(self, df: pd.DataFrame, column: str, problematic_value: Optional[str] = None) -> Optional[RecoveryResult]:
        """Aplica uma limpeza na coluna, convertendo valores não numéricos para NaN."""
        logger.info(f"🛠️ [DataTypeRecoveryAgent] Aplicando limpeza na coluna '{column}'...")
        
        new_df = df.copy()
        
        if problematic_value:
            # Se temos o valor exato, substituímos ele especificamente
            new_df[column] = new_df[column].astype(str).replace(problematic_value, pd.NA, regex=False)
        else:
            # Se não temos o valor, tentamos uma limpeza mais genérica para converter para numérico
            new_df[column] = pd.to_numeric(new_df[column], errors='coerce')
            return RecoveryResult(
                success=True,
                corrected_data=new_df,
                message=f"Coluna '{column}' limpa via conversão forçada para numérico."
            )
        
        # Após a substituição, tentamos a conversão numérica definitiva
        new_df[column] = pd.to_numeric(new_df[column], errors='coerce')
        
        return RecoveryResult(
            success=True,
            corrected_data=new_df,
            message=f"Coluna '{column}' limpa (valor '{problematic_value}' convertido para NaN) para permitir continuidade."
        )
