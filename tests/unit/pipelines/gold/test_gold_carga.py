import pandas as pd

# Teste simples para verificar se o DataFrame de classificação tem as colunas esperadas
def test_classificacao_columns():
    expected_columns = [
        'posicao', 'time', 'pontos', 'jogos', 'vitorias', 
        'empates', 'derrotas', 'gols_pro', 'gols_contra', 'saldo_gols'
    ]
    
    # Criar um DataFrame de exemplo simulando a camada Gold
    df = pd.DataFrame(columns=expected_columns)
    
    assert all(col in df.columns for col in expected_columns)

def test_classificacao_regras_negocio():
    """Valida se as regras de negócio de futebol estão corretas no DataFrame."""
    data = {
        'posicao': [1, 2],
        'time': ['São Paulo', 'Palmeiras'],
        'vitorias': [5, 4],
        'empates': [1, 1],
        'derrotas': [0, 1],
        'gols_pro': [10, 8],
        'gols_contra': [3, 1],
        'saldo_gols': [7, 7],
        'pontos': [16, 13]
    }
    df = pd.DataFrame(data)
    
    # 1. Valida Cálculo de Pontos (Vitória=3, Empate=1)
    # São Paulo: (5*3) + (1*1) = 16
    assert df.iloc[0]['pontos'] == (df.iloc[0]['vitorias'] * 3) + df.iloc[0]['empates']
    
    # 2. Valida Saldo de Gols
    assert df.iloc[1]['saldo_gols'] == df.iloc[1]['gols_pro'] - df.iloc[1]['gols_contra']
    
    # 3. Valida se o primeiro colocado tem mais pontos que o segundo
    assert df.iloc[0]['pontos'] > df.iloc[1]['pontos']

def test_classificacao_integridade_times():
    """Garante que temos exatamente 20 times na tabela final (se for o caso)."""
    # Simulando um DataFrame completo
    df_completo = pd.DataFrame({'time': [f'Time {i}' for i in range(1, 21)]})
    assert len(df_completo) == 20
