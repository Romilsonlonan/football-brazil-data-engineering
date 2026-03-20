"""
DAG Silver - Classificação Tratada
===================================
Pipeline de limpeza e tratamento dos dados de classificação do Brasileirão.

Esta DAG processa dados da camada Bronze para Silver usando Task Groups e Tags
para melhor organização e monitoramento.

Tags: silver, lakehouse, football, classificacao, cleaning
"""

from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.decorators import task
from airflow.decorators import task_group


# Configuração padrão da DAG
default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="silver_classificacao_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 6 * * *",  # Executa diariamente às 6:00
    catchup=False,
    tags=["silver", "lakehouse", "football", "classificacao"],
    default_args=default_args,
    description="Pipeline de limpeza dos dados de classificação do Brasileirão"
) as dag:
    """
    Pipeline Silver para processamento de dados de classificação.
    
    Fluxo:
    1. Executa pipeline de limpeza (classificacao_tratada.py)
    2. Valida os dados processados
    3. Gera relatório de qualidade
    """
    
    @task_group(
        group_id="bronze_to_silver_classificacao",
        tooltip="Processa dados de classificação da Bronze para Silver"
    )
    def bronze_to_silver_classificacao():
        """Grupo de tarefas para processamento de classificação."""
        
        @task(
            task_id="run_classificacao_pipeline",
            retries=2
        )
        def run_classificacao_pipeline() -> str:
            """Executa o pipeline de limpeza de classificação."""
            import sys
            import os
            # Adicionar o caminho do projeto ao sys.path
            # O volume src é montado em /opt/airflow/src no container Airflow
            project_root = os.environ.get('AIRFLOW_PROJECT_ROOT', '/opt/airflow')
            sys.path.insert(0, project_root)
            
            # Import local para evitar lentidão no carregamento do DAG
            from src.pipelines.silver.classificacao_tratada import run
            
            logger = logging.getLogger(__name__)
            logger.info("Iniciando pipeline de classificacao...")
            output_path = run()
            logger.info(f"Pipeline concluido: {output_path}")
            
            return str(output_path)
        
        
        @task(
            task_id="validate_silver_classificacao"
        )
        def validate_silver_classificacao(file_path: str) -> dict:
            """Valida os dados processados na camada Silver."""
            import pandas as pd
            
            logger = logging.getLogger(__name__)
            logger.info(f"Validando dados em: {file_path}")
            
            df = pd.read_parquet(file_path)
            
            # Validações de qualidade
            validations = {
                "not_empty": len(df) > 0,
                "no_nulls": df.isnull().sum().sum() == 0,
                "has_required_columns": all(col in df.columns for col in ['Posição', 'Time', 'Pontos']),
                "positive_points": (df['Pontos'] >= 0).all() if 'Pontos' in df.columns else True,
            }
            
            # Log dos resultados
            for check, result in validations.items():
                status = "OK" if result else "FALHA"
                logger.info(f"{status} {check}: {result}")
            
            # Verificar se todas as validações passaram
            all_passed = all(validations.values())
            
            if all_passed:
                logger.info(f"Validacao concluida: {len(df)} linhas processadas com sucesso!")
            else:
                logger.error("Validacoes falharam!")
                raise ValueError("Validações de qualidade não passaram")
            
            return {
                "rows": len(df),
                "file_path": file_path,
                "validations": validations
            }
        
        
        @task(
            task_id="generate_quality_report"
        )
        def generate_quality_report(validation_result: dict) -> dict:
            """Gera relatório de qualidade dos dados processados."""
            from datetime import datetime
            
            logger = logging.getLogger(__name__)
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "dag_id": "silver_classificacao_pipeline",
                "data_layer": "silver",
                "table": "classificacao",
                "rows_processed": validation_result.get("rows", 0),
                "file_path": validation_result.get("file_path", ""),
                "validation_results": validation_result.get("validations", {}),
                "status": "SUCCESS" if all(validation_result.get("validations", {}).values()) else "FAILED"
            }
            
            logger.info("=" * 50)
            logger.info("RELATORIO DE QUALIDADE - SILVER")
            logger.info("=" * 50)
            logger.info(f"Tabela: classificacao")
            logger.info(f"Linhas processadas: {report['rows_processed']}")
            logger.info(f"Status: {report['status']}")
            logger.info("=" * 50)
            
            return report
        
        # Definir dependências entre tarefas
        file_path = run_classificacao_pipeline()
        validation_result = validate_silver_classificacao(file_path)
        generate_quality_report(validation_result)
    
    
    # Executar o grupo de tarefas
    bronze_to_silver_classificacao()
