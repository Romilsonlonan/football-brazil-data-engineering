"""
DAG Bronze + Silver + Gold - Carga Completa
============================================
Executa todas as camadas: Bronze → Silver → Gold
para regenerar os dados do zero.

Tags: bronze, silver, gold, carga, completo
"""

from datetime import datetime, timedelta
import logging
import os

from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable


default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

logger = logging.getLogger(__name__)


def get_project_root():
    return os.environ.get("AIRFLOW_PROJECT_ROOT", "/opt/airflow")


with DAG(
    dag_id="carga_completa_regeneracao",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,  # Manual apenas
    catchup=False,
    tags=["bronze", "silver", "gold", "carga", "regeneracao"],
    default_args=default_args,
    description="Carga completa: Bronze → Silver → Gold (regenera dados)",
) as dag:
    project_root = get_project_root()

    @task(task_id="bronze_classificacao")
    def run_bronze_classificacao():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Bronze - Classificação")

        from src.pipelines.bronze.classificacao import ClassificacaoBronzePipeline

        pipeline = ClassificacaoBronzePipeline()
        result = pipeline.run()

        logger.info(f"✅ Bronze Classificação: {result}")
        return result

    @task(task_id="bronze_elenco")
    def run_bronze_elenco():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Bronze - Elenco")

        from src.pipelines.bronze.elenco import ElencoBronzePipeline

        pipeline = ElencoBronzePipeline()
        result = pipeline.run()

        logger.info(f"✅ Bronze Elenco: {result}")
        return result

    @task(task_id="bronze_elenco_goleiros")
    def run_bronze_elenco_goleiros():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Bronze - Elenco Goleiros")

        from src.pipelines.bronze.elenco_goleiros import ElencoGoleirosBronzePipeline

        pipeline = ElencoGoleirosBronzePipeline()
        result = pipeline.run()

        logger.info(f"✅ Bronze Elenco Goleiros: {result}")
        return result

    @task(task_id="bronze_elenco_jogadores_campo")
    def run_bronze_elenco_jogadores_campo():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Bronze - Elenco Jogadores Campo")

        from src.pipelines.bronze.elenco_jogadores_campo import (
            ElencoJogadoresCampoBronzePipeline,
        )

        pipeline = ElencoJogadoresCampoBronzePipeline()
        result = pipeline.run()

        logger.info(f"✅ Bronze Elenco Jogadores Campo: {result}")
        return result

    @task(task_id="bronze_calendario")
    def run_bronze_calendario():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Bronze - Calendário")

        from src.pipelines.bronze.calendario_bronze import CalendarioBronzePipeline
        from datetime import datetime as dt

        pipeline = CalendarioBronzePipeline()
        result = pipeline.run(month=dt.now().month, year=dt.now().year)

        logger.info(f"✅ Bronze Calendário: {result}")
        return result

    @task(task_id="silver_classificacao")
    def run_silver_classificacao():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Silver - Classificação")

        from src.pipelines.silver.classificacao_tratada import run as run_silver

        result = run_silver()

        logger.info(f"✅ Silver Classificação: {result}")
        return result

    @task(task_id="silver_elenco")
    def run_silver_elenco():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Silver - Elenco")

        from src.pipelines.silver.elenco_tratado import run as run_silver

        result = run_silver()

        logger.info(f"✅ Silver Elenco: {result}")
        return result

    @task(task_id="silver_elenco_goleiros")
    def run_silver_elenco_goleiros():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Silver - Elenco Goleiros")

        from src.pipelines.silver.elenco_goleiros_transformados import run as run_silver

        result = run_silver()

        logger.info(f"✅ Silver Elenco Goleiros: {result}")
        return result

    @task(task_id="silver_elenco_jogadores_campo")
    def run_silver_elenco_jogadores_campo():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Silver - Elenco Jogadores Campo")

        from src.pipelines.silver.elenco_jogadores_campo_tratados import (
            run as run_silver,
        )

        result = run_silver()

        logger.info(f"✅ Silver Elenco Jogadores Campo: {result}")
        return result

    @task(task_id="silver_calendario")
    def run_silver_calendario():
        import sys

        sys.path.insert(0, project_root)

        logger = logging.getLogger(__name__)
        logger.info("🔄 Executando Silver - Calendário")

        from src.pipelines.silver.calendario_silver import run as run_silver

        result = run_silver()

        logger.info(f"✅ Silver Calendário: {result}")
        return result

    # Executar Bronze (paralelo)
    bronze_result = [
        run_bronze_classificacao(),
        run_bronze_elenco(),
        run_bronze_elenco_goleiros(),
        run_bronze_elenco_jogadores_campo(),
        run_bronze_calendario(),
    ]

    # Executar Silver após Bronze (paralelo)
    silver_result = [
        run_silver_classificacao(),
        run_silver_elenco(),
        run_silver_elenco_goleiros(),
        run_silver_elenco_jogadores_campo(),
        run_silver_calendario(),
    ]

    # Executar Bronze primeiro, depois Silver
    for b in bronze_result:
        b >> silver_result
