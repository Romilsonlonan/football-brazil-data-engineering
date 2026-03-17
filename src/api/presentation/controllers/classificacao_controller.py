"""Controller para classificação."""

from typing import Dict, List, Optional

from src.api.domain.entities.classificacao import Classificacao
from src.api.domain.entities.vagas import VagasConfig
from src.api.infrastructure.repositories.parquet_repository import ParquetClassificacaoRepository


class ClassificacaoController:
    """Controller para operações de classificação."""
    
    def __init__(self):
        self._repository = ParquetClassificacaoRepository()
    
    def listar_classificacao(
        self, 
        temporada: str = "2026",
        zona: Optional[str] = None
    ) -> Dict:
        """
        Lista a classificação completa ou filtrada por zona.
        
        Args:
            temporada: Ano da temporada
            zona: Filtrar por zona (LIBRERTADORES, SUL-AMERICANA, REBAIXAMENTO)
        
        Returns:
            Dicionário com classificação e metadados
        """
        if zona:
            classificacao = self._filtrar_por_zona(zona, temporada)
        else:
            classificacao = self._repository.get_all(temporada)
        
        vagas_config = self._repository.get_vagas_config(temporada)
        
        return {
            "success": True,
            "data": {
                "temporada": temporada,
                "classificacao": [self._to_dict(c) for c in classificacao],
                "vagas": vagas_config.to_dict(),
                "total_times": len(classificacao)
            }
        }
    
    def _filtrar_por_zona(
        self, 
        zona: str, 
        temporada: str
    ) -> List[Classificacao]:
        """Filtra a classificação por zona."""
        zona_upper = zona.upper()
        
        if "LIBERTADORES" in zona_upper or "G" in zona_upper:
            return self._repository.get_times_liberadores(temporada)
        elif "REBAIXAMENTO" in zona_upper:
            return self._repository.get_times_rebaixados(temporada)
        elif "SUL" in zona_upper:
            # Retorna times do 6º ao 11º
            all_times = self._repository.get_all(temporada)
            return [c for c in all_times if 6 <= c.posicao <= 11]
        
        return self._repository.get_all(temporada)
    
    def buscar_por_posicao(
        self, 
        posicao: int, 
        temporada: str = "2026"
    ) -> Dict:
        """Busca a classificação de uma posição específica."""
        classificacao = self._repository.get_by_posicao(posicao, temporada)
        
        if not classificacao:
            return {
                "success": False,
                "error": f"Posição {posicao} não encontrada"
            }
        
        vagas_config = self._repository.get_vagas_config(temporada)
        
        return {
            "success": True,
            "data": {
                **self._to_dict(classificacao),
                "zona": vagas_config.get_zona_por_posicao(posicao)
            }
        }
    
    def buscar_por_time(
        self, 
        nome_time: str, 
        temporada: str = "2026"
    ) -> Dict:
        """Busca a classificação de um time específico."""
        classificacao = self._repository.get_by_time(nome_time, temporada)
        
        if not classificacao:
            return {
                "success": False,
                "error": f"Time '{nome_time}' não encontrado"
            }
        
        vagas_config = self._repository.get_vagas_config(temporada)
        
        return {
            "success": True,
            "data": {
                **self._to_dict(classificacao),
                "zona": vagas_config.get_zona_por_posicao(classificacao.posicao)
            }
        }
    
    def get_vagas(self, temporada: str = "2026") -> Dict:
        """Retorna a configuração de vagas para a temporada."""
        vagas_config = self._repository.get_vagas_config(temporada)
        
        return {
            "success": True,
            "data": vagas_config.to_dict()
        }
    
    def _to_dict(self, classificacao: Classificacao) -> dict:
        """Converte entidade para dicionário."""
        return {
            "posicao": classificacao.posicao,
            "time": classificacao.time.nome,
            "time_reduzido": classificacao.time.nome_reduzido,
            "jogos": classificacao.jogos,
            "vitorias": classificacao.vitorias,
            "empates": classificacao.empates,
            "derrotas": classificacao.derrotas,
            "gp": classificacao.gp,
            "gc": classificacao.gc,
            "sg": classificacao.sg,
            "pontos": classificacao.pontos,
            "aproveitamento": classificacao.aproveitamento,
            "status": classificacao.get_status()
        }
