"""Use Case: Criar Classificação."""

from typing import Optional

from src.api.domain.entities.classificacao import Classificacao
from src.api.domain.entities.time import Time
from src.api.domain.repositories.interface import IClassificacaoRepository


class CriarClassificacaoUseCase:
    """Use case para criar uma classificação."""
    
    def __init__(self, repository: IClassificacaoRepository):
        self._repository = repository
    
    def execute(
        self,
        posicao: int,
        nome_time: str,
        jogos: int = 0,
        vitorias: int = 0,
        empates: int = 0,
        derrotas: int = 0,
        gp: int = 0,
        gc: int = 0,
        sg: Optional[int] = None,
        pontos: Optional[int] = None,
        temporada: Optional[str] = None
    ) -> Classificacao:
        """
        Cria uma nova classificação para um time.
        
        Args:
            posicao: Posição na tabela
            nome_time: Nome do time
            jogos: Número de jogos
            vitorias: Número de vitórias
            empates: Número de empates
            derrotas: Número de derrotas
            gp: Gols pró
            gc: Gols contra
            sg: Saldo de gol (opcional - calculado automaticamente)
            pontos: Pontos (opcional - calculado automaticamente)
            temporada: Ano da temporada
        
        Returns:
            Nova classificação criada
        """
        # Cria a entidade Time
        time = Time(nome=nome_time)
        
        # Calcula saldo de gol se não fornecido
        if sg is None:
            sg = gp - gc
        
        # Calcula pontos se não fornecido
        if pontos is None:
            pontos = (vitorias * 3) + (empates * 1)
        
        # Cria a entidade Classificacao
        classificacao = Classificacao(
            posicao=posicao,
            time=time,
            jogos=jogos,
            vitorias=vitorias,
            empates=empates,
            derrotas=derrotas,
            gp=gp,
            gc=gc,
            sg=sg,
            pontos=pontos,
            temporada=temporada
        )
        
        # Aqui seria a chamada para salvar no repositório
        # Por enquanto retornamos a entidade criada
        return classificacao
