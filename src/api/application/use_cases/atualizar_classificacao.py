"""Use Case: Atualizar Classificação."""

from typing import Optional

from src.api.domain.entities.classificacao import Classificacao
from src.api.domain.repositories.interface import IClassificacaoRepository


class AtualizarClassificacaoUseCase:
    """Use case para atualizar uma classificação existente."""

    def __init__(self, repository: IClassificacaoRepository):
        self._repository = repository

    def execute(
        self,
        posicao: int,
        jogos: Optional[int] = None,
        vitorias: Optional[int] = None,
        empates: Optional[int] = None,
        derrotas: Optional[int] = None,
        gp: Optional[int] = None,
        gc: Optional[int] = None,
        sg: Optional[int] = None,
        pontos: Optional[int] = None,
        temporada: Optional[str] = None,
    ) -> Classificacao:
        """
        Atualiza uma classificação existente.

        Args:
            posicao: Posição na tabela (identificador)
            jogos: Novo número de jogos
            vitorias: Novo número de vitórias
            empates: Novo número de empates
            derrotas: Novo número de derrotas
            gp: Novos gol pró
            gc: Novos gol contra
            sg: Novo saldo de gol
            pontos: Novos pontos
            temporada: Ano da temporada

        Returns:
            Classificação atualizada
        """
        # Busca a classificação atual
        classificacao_atual = self._repository.get_by_posicao(posicao, temporada)

        if not classificacao_atual:
            raise ValueError(f"Classificação não encontrada na posição {posicao}")

        # Atualiza os campos fornecidos
        if jogos is not None:
            classificacao_atual.jogos = jogos
        if vitorias is not None:
            classificacao_atual.vitorias = vitorias
        if empates is not None:
            classificacao_atual.empates = empates
        if derrotas is not None:
            classificacao_atual.derrotas = derrotas
        if gp is not None:
            classificacao_atual.gp = gp
        if gc is not None:
            classificacao_atual.gc = gc

        # Recalcula saldo de gol se GP ou GC foram atualizados
        if gp is not None or gc is not None:
            classificacao_atual.sg = classificacao_atual.gp - classificacao_atual.gc

        # Recalcula pontos se V, E ou D foram atualizados
        if vitorias is not None or empates is not None or derrotas is not None:
            classificacao_atual.pontos = (
                classificacao_atual.vitorias * 3
            ) + classificacao_atual.empates

        # Atualiza pontos explicitamente se fornecido
        if pontos is not None:
            classificacao_atual.pontos = pontos

        return classificacao_atual
