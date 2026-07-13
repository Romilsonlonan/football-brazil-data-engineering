import pytest
from src.infrastructure.metadata.memory_metadata_service import MemoryMetadataService

@pytest.fixture
def metadata_service():
    return MemoryMetadataService()

def test_register_and_get_metadata(metadata_service):
    schema = {"id": "int", "name": "string", "age": "int"}
    descriptions = {"name": "Nome do jogador", "age": "Idade do jogador"}
    
    metadata_service.register_table("players", schema, descriptions)
    
    metadata = metadata_service.get_table_metadata("players")
    
    assert metadata is not None
    assert metadata["schema"] == schema
    assert metadata["descriptions"] == descriptions

def test_search_metadata(metadata_service):
    schema = {"id": "int", "name": "string", "age": "int"}
    descriptions = {"name": "Nome do jogador", "age": "Idade do jogador"}
    metadata_service.register_table("players", schema, descriptions)
    metadata_service.register_table("matches", {"id": "int", "date": "date"}, {"date": "Data da partida"})

    # Busca por nome da tabela
    results = metadata_service.search_metadata("players")
    assert len(results) == 1
    assert results[0]["table_name"] == "players"

    # Busca por descrição de coluna
    results = metadata_service.search_metadata("partida")
    assert len(results) == 1
    assert results[0]["table_name"] == "matches"

    # Busca por coluna inexistente
    results = metadata_service.search_metadata("non_existent")
    assert len(results) == 0
