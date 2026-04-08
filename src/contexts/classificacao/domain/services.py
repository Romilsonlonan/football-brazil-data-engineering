"""Domain Services para Classificação

Este módulo contém as REGRAS DE NEGÓCIO do domínio de classificação.
Aqui fica a lógica que antes estava dispersa em pipelines e entidades.

Princípios DDD:
- Domain Services contêm regras de negócio
- Entities devem ser 'anêmicas' (só dados)
- Value Objects são imutáveis e validam-se
"""

from dataclasses import dataclass

from .value_objects import Pontos, Posicao, Aproveitamento
from .entities import Time, Classificacao, ResultadoJogo


class CalculadoraClassificacao:
    """Domain Service que calcula métricas de classificação.

    Conforme DDD, as regras de negócio devem estar aqui,
    não nas entidades ou nos pipelines.
    """

    def calcular_aproveitamento(self, classificacao: Classificacao) -> Aproveitamento:
        """Calcula o aproveitamento percentual do time.

        Fórmula: (pontos / jogos * 3) * 100
        """
        if classificacao.jogos == 0:
            return Aproveitamento(0.0)

        pontos_possiveis = classificacao.jogos * 3
        aproveitamento = (classificacao.pontos / pontos_possiveis) * 100
        return Aproveitamento(round(aproveitamento, 2))

    def calcular_pontos_resultado(self, resultado: ResultadoJogo, time: str) -> Pontos:
        """Calcula os pontos ganhos por um time em um resultado."""
        if resultado.empatou:
            return Pontos.por_empate()

        if resultado.mandante_venceu and resultado.time_casa == time:
            return Pontos.por_vitoria()

        if resultado.visitante_venceu and resultado.time_fora == time:
            return Pontos.por_vitoria()

        return Pontos.por_derrota()

    def calcular_saldo_gols(self, classificacao: Classificacao) -> int:
        """Retorna o saldo de gols."""
        return classificacao.saldo_goals

    def validar_classificacao(self, classificacao: Classificacao) -> bool:
        """Valida se uma classificação é consistente."""
        if classificacao.jogos < 0:
            return False
        if classificacao.pontos < 0:
            return False
        if classificacao.jogos > 38:  # Brasileirão tem 38 rodadas
            return False

        jogos_obrigatorios = (
            classificacao.vitorias + classificacao.empates + classificacao.derrotas
        )
        if jogos_obrigatorios != classificacao.jogos:
            return False

        pontos_obrigatorios = classificacao.vitorias * 3 + classificacao.empates * 1
        if pontos_obrigatorios != classificacao.pontos:
            return False

        return True


class CalculadoraColocacao:
    """Domain Service que calcula a colocação dos times."""

    def __init__(self):
        self._classificacoes: list[Classificacao] = []

    def adicionar(self, classificacao: Classificacao) -> None:
        """Adiciona uma classificação para ordenação."""
        self._classificacoes.append(classificacao)

    def ordenar(self) -> list[Classificacao]:
        """Retorna as classificações ordenadas por critérios de desempate."""
        return sorted(
            self._classificacoes,
            key=lambda c: (
                -c.pontos,
                -c.saldo_goals,
                -c.goals_pro,
            ),
        )

    def posicao(self, time: str) -> Posicao | None:
        """Retorna a posição de um time."""
        ordenadas = self.ordenar()
        for i, c in enumerate(ordenadas, start=1):
            if c.time == time:
                return Posicao(i)
        return None

    def top_4(self) -> list[Classificacao]:
        """Retorna os 4 primeiros (classificados para Libertadores)."""
        return self.ordenar()[:4]

    def zona_sula(self) -> Posicao:
        """Retorna a posição inicial da zona de rebaixamento (17º)."""
        return Posicao(17)

    def rebaixados(self) -> list[Classificacao]:
        """Retorna os 4 últimos (rebaixados)."""
        return self.ordenar()[-4:]


@dataclass
class Confronto:
    """Value Object para representar um confronto diretos."""

    time_a: str
    time_b: str
    pontos_a: int = 0
    pontos_b: int = 0
    vitorias_a: int = 0
    vitorias_b: int = 0
    empates: int = 0

    @property
    def resultado(self) -> str:
        if self.pontos_a > self.pontos_b:
            return f"{self.time_a} lidera"
        if self.pontos_b > self.pontos_a:
            return f"{self.time_b} lidera"
        return "empate técnico"


class CalculadoraConfrontosDiretos:
    """Domain Service para calcular confrontos diretos entre times."""

    def calcular(
        self, classificacoes: list[Classificacao], time_a: str, time_b: str
    ) -> Confronto:
        """Calcula o confronto direto entre dois times."""
        c_a = next((c for c in classificacoes if c.time == time_a), None)
        c_b = next((c for c in classificacoes if c.time == time_b), None)

        if not c_a or not c_b:
            raise ValueError(f"Time não encontrado: {time_a} ou {time_b}")

        return Confronto(
            time_a=time_a,
            time_b=time_b,
            pontos_a=c_a.pontos,
            pontos_b=c_b.pontos,
            vitorias_a=c_a.vitorias,
            vitorias_b=c_b.vitorias,
        )
