from pathlib import Path
import pandas as pd
from src.pipelines.bronze.base import BasePipeline
from src.pipelines.recovery.schema_recovery_agent import SchemaRecoveryAgent
from src.pipelines.recovery.data_type_recovery_agent import DataTypeRecoveryAgent

class MockBrokenPipeline(BasePipeline):
    def __init__(self, name="test_pipeline", error_type="schema"):
        super().__init__(name)
        self.error_type = error_type

    def extract(self, **kwargs) -> pd.DataFrame:
        return pd.DataFrame({"col1": [1, 2], "col2": [3, 4], "col_missing": [10, 20]})

    def transform(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        if self.error_type == "schema":
            # Simula erro de coluna ausente
            return df[["col1", "col_missing_error"]]
        elif self.error_type == "datatype":
            # Simula erro de conversão de tipo (ex: converter 'N/A' para float)
            df["col_numeric"] = ["1.0", "N/A"]
            return df.astype({"col_numeric": float})
        return df

    def load(self, df: pd.DataFrame, **kwargs) -> Path:
        return Path("dummy.parquet")

def test_schema_recovery():
    pipeline = MockBrokenPipeline(error_type="schema")
    agent = SchemaRecoveryAgent()
    output_path = pipeline.run(recovery_agent=agent)
    assert output_path == Path("dummy.parquet")
    print("\n✅ Teste de recuperação de schema passou!")

def test_datatype_recovery():
    pipeline = MockBrokenPipeline(error_type="datatype")
    agent = DataTypeRecoveryAgent()
    output_path = pipeline.run(recovery_agent=agent)
    assert output_path == Path("dummy.parquet")
    print("\n✅ Teste de recuperação de datatype passou!")

if __name__ == "__main__":
    test_schema_recovery()
    test_datatype_recovery()
