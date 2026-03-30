"""Base Pipeline - Bronze Layer."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.utils.logger import logger


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
    
    def run(self, **kwargs) -> Path:
        """Execute the complete ETL pipeline.
        
        Returns:
            Path to the saved output file.
        """
        logger.info("=" * 60)
        logger.info(f"INICIANDO PIPELINE - {self.pipeline_name.upper()}")
        logger.info("=" * 60)
        
        try:
            # Extract
            df = self.extract(**kwargs)
            
            # Transform
            df = self.transform(df, **kwargs)
            
            # Load
            output_path = self.load(df, **kwargs)
            
            logger.info("=" * 60)
            logger.info(f"PIPELINE {self.pipeline_name.upper()} CONCLUIDO")
            logger.info("=" * 60)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise