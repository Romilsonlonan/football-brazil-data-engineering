"""
Observabilidade de Pipeline - Lakehouse Brasileiro
====================================================

Este módulo implementa monitoramento e observabilidade de pipelines
com logging estruturado, métricas e alertas.

Características:
- Monitoramento de execução de pipelines
- Métricas de performance
- Rastreamento de erros
- Alertas em tempo real
- Integração com logs estruturados

Usage:
    from src.security.log_observer import PipelineMonitor, LogObserver

    monitor = PipelineMonitor()
    with monitor.track("meu_pipeline"):
        # código do pipeline
        pass
"""

import time
import traceback
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from contextlib import contextmanager

from src.utils.logger import logger


@dataclass
class PipelineMetrics:
    """Métricas de execução de um pipeline."""

    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    status: str = "running"  # running, success, failed, timeout
    rows_processed: int = 0
    rows_failed: int = 0
    memory_used_mb: float = 0.0
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    warnings: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": round(self.duration_seconds, 2),
            "status": self.status,
            "rows_processed": self.rows_processed,
            "rows_failed": self.rows_failed,
            "memory_used_mb": round(self.memory_used_mb, 2),
            "error_message": self.error_message,
            "warnings_count": len(self.warnings),
            "metadata": self.metadata,
        }


class PipelineMonitor:
    """
    Monitor de pipelines com métricas e alertas.

    Example:
        >>> monitor = PipelineMonitor()
        >>> with monitor.track("bronze_classificacao"):
        ...     # seu código
        ...     pass
        >>>
        >>> # Ver métricas
        >>> metrics = monitor.get_metrics("bronze_classificacao")
    """

    def __init__(self):
        self._metrics_history: Dict[str, PipelineMetrics] = {}
        self._active_pipelines: Dict[str, PipelineMetrics] = {}

    @contextmanager
    def track(self, pipeline_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager para rastrear um pipeline.

        Args:
            pipeline_name: Nome do pipeline
            metadata: Metadados adicionais

        Usage:
            monitor = PipelineMonitor()
            with monitor.track("processar_dados"):
                df = load_data()
                process(df)
        """
        metrics = PipelineMetrics(
            name=pipeline_name, start_time=datetime.now(), metadata=metadata or {}
        )

        self._active_pipelines[pipeline_name] = metrics

        logger.info("=" * 60)
        logger.info(f"🚀 INICIANDO PIPELINE: {pipeline_name}")
        logger.info(f"   Timestamp: {metrics.start_time.isoformat()}")
        if metadata:
            for key, value in metadata.items():
                logger.info(f"   {key}: {value}")
        logger.info("=" * 60)

        start_time = time.time()

        try:
            yield metrics

            # Sucesso
            metrics.end_time = datetime.now()
            metrics.duration_seconds = time.time() - start_time
            metrics.status = "success"

            logger.info("=" * 60)
            logger.info(f"✅ PIPELINE CONCLUÍDO: {pipeline_name}")
            logger.info(f"   Duração: {metrics.duration_seconds:.2f}s")
            logger.info(f"   Linhas processadas: {metrics.rows_processed}")
            logger.info("=" * 60)

        except Exception as e:
            # Falha
            metrics.end_time = datetime.now()
            metrics.duration_seconds = time.time() - start_time
            metrics.status = "failed"
            metrics.error_message = str(e)
            metrics.error_traceback = traceback.format_exc()

            logger.error("=" * 60)
            logger.error(f"❌ PIPELINE FALHOU: {pipeline_name}")
            logger.error(f"   Erro: {str(e)}")
            logger.error(f"   Duração: {metrics.duration_seconds:.2f}s")
            logger.error("=" * 60)
            logger.error(f"Traceback:\n{metrics.error_traceback}")

            raise

        finally:
            # Armazenar métricas
            self._metrics_history[pipeline_name] = metrics
            if pipeline_name in self._active_pipelines:
                del self._active_pipelines[pipeline_name]

    def track_function(self, pipeline_name: str = None):
        """
        Decorador para rastrear funções como pipelines.

        Usage:
            @monitor.track_function("minha_funcao")
            def minha_funcao():
                pass
        """

        def decorator(func: Callable) -> Callable:
            name = pipeline_name or func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.track(name):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_metrics(self, pipeline_name: str) -> Optional[PipelineMetrics]:
        """Retorna as métricas do último pipeline executado."""
        return self._metrics_history.get(pipeline_name)

    def get_all_metrics(self) -> Dict[str, PipelineMetrics]:
        """Retorna todas as métricas históricas."""
        return self._metrics_history.copy()

    def get_summary(self) -> Dict:
        """Retorna um resumo de todos os pipelines."""
        total = len(self._metrics_history)
        success = sum(1 for m in self._metrics_history.values() if m.is_success)
        failed = sum(1 for m in self._metrics_history.values() if m.is_failed)

        total_duration = sum(m.duration_seconds for m in self._metrics_history.values())
        avg_duration = total_duration / total if total > 0 else 0

        return {
            "total_pipelines": total,
            "successful": success,
            "failed": failed,
            "success_rate": round(success / total * 100, 1) if total > 0 else 0,
            "total_duration_seconds": round(total_duration, 2),
            "average_duration_seconds": round(avg_duration, 2),
            "pipelines": [m.to_dict() for m in self._metrics_history.values()],
        }

    def log_summary(self):
        """Imprime um resumo dos pipelines no logger."""
        summary = self.get_summary()

        logger.info("=" * 60)
        logger.info("📊 RESUMO DE PIPELINES")
        logger.info("=" * 60)
        logger.info(f"Total executados: {summary['total_pipelines']}")
        logger.info(f"Sucesso: {summary['successful']} ({summary['success_rate']}%)")
        logger.info(f"Falhas: {summary['failed']}")
        logger.info(f"Duração total: {summary['total_duration_seconds']}s")
        logger.info(f"Duração média: {summary['average_duration_seconds']}s")
        logger.info("=" * 60)


class LogObserver:
    """
    Observador de logs para pipelines com formatação estruturada.

    Implementa:
    - Logs estruturados em JSON
    - Timestamps precisos
    - Contextos de execução
    - Alertas baseados em regras
    """

    def __init__(self, enable_json: bool = False):
        self.enable_json = enable_json

    def log_pipeline_start(self, pipeline_name: str, params: Optional[Dict] = None):
        """Log de início de pipeline."""
        logger.info(
            f"🚀 PIPELINE_START | " f"name={pipeline_name} | " f"params={params or {}}"
        )

    def log_pipeline_end(
        self, pipeline_name: str, status: str, duration: float, rows: int = 0
    ):
        """Log de fim de pipeline."""
        logger.info(
            f"🏁 PIPELINE_END | "
            f"name={pipeline_name} | "
            f"status={status} | "
            f"duration={duration:.2f}s | "
            f"rows={rows}"
        )

    def log_data_quality(
        self, table_name: str, checks: Dict[str, bool], metrics: Dict[str, Any]
    ):
        """Log de qualidade de dados."""
        passed = sum(1 for v in checks.values() if v)
        total = len(checks)

        logger.info(
            f"📋 DATA_QUALITY | "
            f"table={table_name} | "
            f"passed={passed}/{total} | "
            f"checks={checks}"
        )

        if passed < total:
            logger.warning(
                f"⚠️ QUALITY_CHECKS_FAILED | "
                f"table={table_name} | "
                f"failed_checks={[k for k, v in checks.items() if not v]}"
            )

    def log_security_alert(
        self, alert_type: str, table_name: str, details: Dict[str, Any]
    ):
        """Log de alerta de segurança."""
        logger.critical(
            f"🚨 SECURITY_ALERT | "
            f"type={alert_type} | "
            f"table={table_name} | "
            f"details={details}"
        )

    def log_performance_warning(
        self, pipeline_name: str, metric: str, value: float, threshold: float
    ):
        """Log de aviso de performance."""
        logger.warning(
            f"⚡ PERFORMANCE_WARNING | "
            f"pipeline={pipeline_name} | "
            f"metric={metric} | "
            f"value={value} | "
            f"threshold={threshold}"
        )


# Instância global do monitor
_global_monitor = PipelineMonitor()


def get_monitor() -> PipelineMonitor:
    """Retorna a instância global do monitor."""
    return _global_monitor


# ============================================
# Decoradores Prontos
# ============================================


def monitor_pipeline(pipeline_name: str = None):
    """
    Decorador para monitorar automaticamente funções.

    Usage:
        @monitor_pipeline("processar_dados")
        def processar_dados():
            pass
    """
    return _global_monitor.track_function(pipeline_name)
