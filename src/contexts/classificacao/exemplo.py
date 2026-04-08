"""Exemplo de uso do Domain Service de Classificação

Demonstra como usar o DDD implementado.
"""

from src.contexts.classificacao import (
    Classificacao,
    CalculadoraClassificacao,
    CalculadoraColocacao,
    GerarClassificacaoUseCase,
    Pontos,
    Posicao,
    Aproveitamento,
)


def exemplo_basico():
    """Exemplo básico de uso."""
    print("=" * 60)
    print("📊 EXEMPLO: CalculadoraClassificacao")
    print("=" * 60)

    # Criar entidade
    flamengo = Classificacao(
        time="Flamengo",
        pontos=21,
        jogos=10,
        vitorias=6,
        empates=3,
        derrotas=1,
        goals_pro=18,
        goals_contra=8,
        saldo_goals=10,
    )

    # Usar Domain Service
    calculadora = CalculadoraClassificacao()
    aproveitamento = calculadora.calcular_aproveitamento(flamengo)

    print(f"\nTime: {flamengo.time}")
    print(f"Pontos: {flamengo.pontos}")
    print(f"Jogos: {flamengo.jogos}")
    print(f"Aproveitamento: {aproveitamento}")
    print(f"  Emoji: {aproveitamento.emoji}")

    # Validar
    e_valido = calculadora.validar_classificacao(flamengo)
    print(f"\nClassificação válida: {e_valido}")


def exemplo_colocacao():
    """Exemplo de cálculo de colocação."""
    print("\n" + "=" * 60)
    print("📊 EXEMPLO: CalculadoraColocacao")
    print("=" * 60)

    # Criar classificações
    times = [
        Classificacao("Flamengo", 21, 10, 6, 3, 1, 18, 8, 10),
        Classificacao("Palmeiras", 20, 10, 6, 2, 2, 15, 10, 5),
        Classificacao("Atlético-MG", 18, 10, 5, 3, 2, 14, 11, 3),
        Classificacao("Botafogo", 22, 10, 7, 1, 2, 16, 9, 7),
    ]

    # Usar calculadora de colocacao
    calc_colocacao = CalculadoraColocacao()
    for t in times:
        calc_colocacao.adicionar(t)

    print("\nClassificação:")
    for i, c in enumerate(calc_colocacao.ordenar(), start=1):
        print(f"  {i}. {c.time} - {c.pontos} pts (SG: {c.saldo_goals})")

    print(f"\nTop 4 Libertadores: {[c.time for c in calc_colocacao.top_4()]}")
    print(f"Rebaixados: {[c.time for c in calc_colocacao.rebaixados()]}")


def exemplo_value_objects():
    """Exemplo de Value Objects."""
    print("\n" + "=" * 60)
    print("📊 EXEMPLO: Value Objects")
    print("=" * 60)

    # Pontos
    pt = Pontos.por_vitoria()
    print(f"\nPontos por vitória: {pt}")

    # Posicao
    pos = Posicao(1)
    print(f"Posição: {pos.valor}")
    print(f"  É líder: {pos.valor == 1}")

    # Aproveitamento
    apr = Aproveitamento(66.67)
    print(f"Aproveitamento: {apr}")
    print(f"  Emoji: {apr.emoji}")


if __name__ == "__main__":
    exemplo_basico()
    exemplo_colocacao()
    exemplo_value_objects()
    print("\n✅ Todos os exemplos executados!")
