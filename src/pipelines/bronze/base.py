"""Base Pipeline - Bronze Layer."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.utils.logger import logger
from src.pipelines.recovery.interfaces import RecoveryAgent, RecoveryResult


class BasePipeline(ABC):
    """Abstract base class for all Bronze pipelines.

    This class defines the interface for ETL pipelines in the Bronze layer.
    The Bronze layer is responsible for extracting raw data from external
    sources and storing it without transformation.
    """

    def __init__(self, pipeline_name: str) -> None:
        """Initialize the base pipeline.

        Args:
            pipeline_name: Name identifier for this pipeline.
        """
        self.pipeline_name = pipeline_name
        logger.info(f"Pipeline '{pipeline_name}' initialized")

    @abstractmethod
    def extract(self, **kwargs) -> pd.DataFrame:
        """Extract data from the source.

        Returns:
            DataFrame with raw extracted data.
        """
        pass

    @abstractmethod
    def transform(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transform the extracted data.

        Args:
            df: Raw DataFrame to transform.

        Returns:
            Transformed DataFrame.
        """
        pass

    @abstractmethod
    def load(self, df: pd.DataFrame, table_name: str = "output", **kwargs) -> Path:
        """Load the data to storage.

        Args:
            df: DataFrame to save.
            table_name: Name for the output table/file.

        Returns:
            Path to the saved file.
        """
        pass

    def run(self, recovery_agent: Optional[RecoveryAgent] = None, **kwargs) -> Path:
        """Execute the complete ETL pipeline with optional self-healing.

        Args:
            recovery_agent: Agent responsible for attempting to recover from errors.
            **kwargs: Arguments passed to extract, transform, and load.

        Returns:
            Path to the saved output file.
        """
        logger.info("=" * 60)
        logger.info(f"INICIANDO PIPELINE - {self.pipeline_name.upper()}")
        logger.info("=" * 60)

        step = "extract"
        df = None

        try:
            # 1. Extract
            df = self.extract(**kwargs)
            step = "transform"

            # 2. Transform
            df = self.transform(df, **kwargs)
            step = "load"

            # 3. Load
            output_path = self.load(df, **kwargs)

            logger.info("=" * 60)
            logger.info(f"PIPELINE {self.pipeline_name.upper()} CONCLUIDO")
            logger.info("=" * 60)

            return output_path

        except Exception as e:
            if recovery_agent:
                logger.warning(f"🚨 Erro detectado no passo '{step}': {e}")
                context = {
                    "step": step,
                    "data": df,
                    "kwargs": kwargs,
                    "pipeline_name": self.pipeline_name
                }

                recovery_result = recovery_agent.attempt_recovery(e, context)

                if recovery_result and recovery_result.success:
                    logger.info(f"✅ Recuperação bem-sucedida: {recovery_result.message}")

                    if step == "extract":
                        df = recovery_result.corrected_data
                        step = "transform"
                        df = self.transform(df, **kwargs)
                        step = "load"
                        return self.load(df, **kwargs)

                    elif step == "transform":
                        df = recovery_result.corrected_data
                        step = "load"
                        return self.load(df, **kwargs)

                    elif step == "load":
                        df = recovery_result.corrected_data
                        return self.load(df, **kwargs)

            logger.error(f"Pipeline failed: {e}")
            raise
