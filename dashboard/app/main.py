"""
Dashboard Principal - Streamlit App
Arquitetura Clean Architecture com Domain-Driven Design
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

import streamlit as st
from pandas import DataFrame

from dashboard.application.use_cases.buscar_classificacao import (
    BuscarClassificacaoUseCase,
)
from dashboard.application.use_cases.buscar_elenco import BuscarElencoUseCase
from dashboard.infrastructure.repositories.parquet_repository import (
    ParquetRepository,
)
from dashboard.shared.config import get_data_path, get_bronze_data_path

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Brasileirão",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# ESTILIZAÇÃO (CSS)
# ==============================================================================
# URL da imagem de fundo (campo de futebol)
CAMPO_URL = "https://i.ibb.co/WwGBp2z/campo.webp"

st.markdown(
    f"""
    <style>
    /* Tema Escuro com imagem de fundo */
    .stApp {{
        background: linear-gradient(135deg, rgba(15, 15, 26, 0.5) 0%, rgba(26, 26, 46, 0.5) 100%),
                    url("{CAMPO_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Container principal com borda */
    .main-content {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }}
    
    /* Cards com gradiente e sombras */
    .metric-card {{
        background: linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }}
    
    .metric-card.highlight {{
        background: linear-gradient(135deg, #0d4f4f 0%, #1a3a5c 100%);
    }}
    
    /* Tabela de classificação */
    .classification-table {{
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 16px;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0d2818 0%, #061810 100%);
        border-right: 1px solid rgba(0, 212, 170, 0.2);
    }}
    
    /* Headers */
    h1, h2, h3 {{
        color: #e0e0e0 !important;
        font-family: 'Inter', sans-serif;
    }}
    
    /* Métricas */
    [data-testid="stMetricValue"] {{
        font-size: 2rem;
        font-weight: bold;
    }}
    
    /*DataFrame */
    [data-testid="stDataFrame"] {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# INSTÂNCIA DO REPOSITÓRIO E USE CASES
# ==============================================================================
@st.cache_data
def get_classificacao_use_case() -> BuscarClassificacaoUseCase:
    """Retorna instância do use case de classificação."""
    repo = ParquetRepository(get_data_path())
    return BuscarClassificacaoUseCase(repo)


@st.cache_data
def get_elenco_use_case() -> BuscarElencoUseCase:
    """Retorna instância do use case de elenco."""
    repo = ParquetRepository(get_bronze_data_path())
    return BuscarElencoUseCase(repo)


# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: #00d4aa; margin-bottom: 0; font-size: 28px;">🏆 Brasileirão</h1>
            <p style="color: #00d4aa; font-size: 20px; font-weight: bold;">Painel de controle 2026</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("---")
    
    # Menu de navegação
    menu = st.radio(
        "📋 Navegação",
        ["🏠 Painel de controle", "📊 Escudo", "👥 Elenco"],
    )
    
    st.markdown("---")
    
    # Filtros
    st.subheader("🔍 Filtros")
    
    # obter lista de times
    elenco_use_case = get_elenco_use_case()
    times = elenco_use_case.get_times()
    
    if menu == "📊 Classificação":
        time_selecionado = st.selectbox(
            "🏟️ Selecione o Time",
            ["Todos"] + times,
        )
    elif menu == "👥 Elenco":
        time_selecionado = st.selectbox(
            "🏟️ Selecione o Time",
            times,
        )
    else:
        time_selecionado = None

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================
def exibir_metricas_time(df: DataFrame, time: str) -> None:
    """Exibe cards de métricas para um time específico."""
    if time == "Todos":
        time_info = df.iloc[0]
    else:
        time_info = df[df["time"].str.contains(time, case=False)].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📍 Posição", f"#{int(time_info['posicao'])}")

    with col2:
        st.metric("⭐ Pontos", f"{int(time_info['pontos'])}")

    with col3:
        st.metric("🏆 Vitórias", f"{int(time_info['vitorias'])}")

    with col4:
        st.metric("⚽ Saldo de Gols", f"{int(time_info['saldo_gols'])}")


def criar_grafico_desempenho(df: DataFrame, time: str) -> None:
    """Cria gráfico de desempenho do time."""
    import plotly.graph_objects as go

    if time == "Todos":
        # Top 5 times
        top_times = df.head(5)
        fig = go.Figure()

        for idx, row in top_times.iterrows():
            fig.add_trace(
                go.Bar(
                    y=[row["time"]],
                    x=[row["vitorias"]],
                    name="Vitórias",
                    marker_color="#00d4aa",
                    orientation="h",
                )
            )
            fig.add_trace(
                go.Bar(
                    y=[row["time"]],
                    x=[row["empates"]],
                    name="Empates",
                    marker_color="#ffd700",
                    orientation="h",
                )
            )
            fig.add_trace(
                go.Bar(
                    y=[row["time"]],
                    x=[row["derrotas"]],
                    name="Derrotas",
                    marker_color="#ff6b6b",
                    orientation="h",
                )
            )

        fig.update_layout(
            title="📈 Top 5 - Desempenho por Tipo de Resultado",
            barmode="stack",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )
    else:
        time_info = df[df["time"].str.contains(time, case=False)].iloc[0]
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=["Vitórias", "Empates", "Derrotas"],
                y=[time_info["vitorias"], time_info["empates"], time_info["derrotas"]],
                marker_color=["#00d4aa", "#ffd700", "#ff6b6b"],
                text=[time_info["vitorias"], time_info["empates"], time_info["derrotas"]],
                textposition="auto",
            )
        )

        fig.update_layout(
            title=f"📈 {time} - Desempeno",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
        )

    st.plotly_chart(fig, width="stretch")


def criar_grafico_pizza(df: DataFrame, time: str) -> None:
    """Cria gráfico de pizza para distribuição de resultados."""
    import plotly.graph_objects as go

    if time == "Todos":
        # Totais gerais
        total_vitorias = df["vitorias"].sum()
        total_empates = df["empates"].sum()
        total_derrotas = df["derrotas"].sum()

        labels = ["Vitórias", "Empates", "Derrotas"]
        values = [total_vitorias, total_empates, total_derrotas]
        colors = ["#00d4aa", "#ffd700", "#ff6b6b"]
    else:
        time_info = df[df["time"].str.contains(time, case=False)].iloc[0]
        labels = ["Vitórias", "Empates", "Derrotas"]
        values = [
            time_info["vitorias"],
            time_info["empates"],
            time_info["derrotas"],
        ]
        colors = ["#00d4aa", "#ffd700", "#ff6b6b"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                hole=0.4,
                textinfo="label+percent",
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        title="🍩 Distribuição de Resultados",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=400,
    )

    st.plotly_chart(fig, width="stretch")


def exibir_tabela_classificacao(df: DataFrame) -> None:
    """Exibe tabela de classificação estilizada."""
    # Criar coluna de zona
    df_display = df.copy()
    df_display["Zona"] = df_display["posicao"].apply(
        lambda x: "🟢 G4" if x <= 4 else ("🔴 Rebaixamento" if x >= 17 else "🟡 Competição")
    )

    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
    )


def exibir_tabela_elenco(df: DataFrame) -> None:
    """Exibe tabela de elenco."""
    # Selecionar colunas relevantes
    colunas_selecionadas = ["Nome", "Time", "Posição", "Idade", "NAC"]

    # Filtrar apenas colunas existentes
    colunas_existentes = [col for col in colunas_selecionadas if col in df.columns]

    df_display = df[colunas_existentes].copy()

    # Renomear colunas para melhor visualização
    df_display.columns = ["Nome", "Time", "Posição", "Idade", "Nacionalidade"][
        : len(colunas_existentes)
    ]

    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
        height=600,
    )


# ==============================================================================
# PÁGINAS
# ==============================================================================
if menu == "🏠 Painel de controle":
    st.markdown('<h1><img src="https://i.ibb.co/0yBYM9HS/bola.png" width="60" style="vertical-align: middle;"/> Painel Geral</h1>', unsafe_allow_html=True)
    st.markdown("Bem-vindo ao Dashboard do Brasileirão 2026!")

    # Carregar dados
    classificacao_use_case = get_classificacao_use_case()
    df_classificacao = classificacao_use_case.execute()

    # Cards de métricas gerais
    st.subheader("📊 Estatísticas Gerais")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📍 Líder", df_classificacao.iloc[0]["time"])

    with col2:
        st.metric("⭐ Total Pontos", f"{int(df_classificacao['pontos'].sum())}")

    with col3:
        st.metric(
            "🏆 Total Vitórias", f"{int(df_classificacao['vitorias'].sum())}"
        )

    with col4:
        st.metric(
            "⚽ Total Gols", f"{int(df_classificacao['gols_pro'].sum())}"
        )

    st.markdown("---")

    # Gráficos
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        criar_grafico_desempenho(df_classificacao, "Todos")

    with col_graf2:
        criar_grafico_pizza(df_classificacao, "Todos")

    st.markdown("---")

    # Tabela de classificação
    st.subheader("📋 Classificação Geral")
    exibir_tabela_classificacao(df_classificacao)


elif menu == "📊 Escudo":
    st.title("📊 Classificação por Time")

    # Carregar dados
    classificacao_use_case = get_classificacao_use_case()
    df_classificacao = classificacao_use_case.execute()

    if time_selecionado and time_selecionado != "Todos":
        # Filtrar time específico
        df_time = df_classificacao[
            df_classificacao["time"].str.contains(time_selecionado, case=False)
        ]

        # Exibir métricas
        st.subheader(f"📊 {time_selecionado}")
        exibir_metricas_time(df_classificacao, time_selecionado)

        st.markdown("---")

        # Gráficos
        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            criar_grafico_desempenho(df_classificacao, time_selecionado)

        with col_graf2:
            criar_grafico_pizza(df_classificacao, time_selecionado)

        st.markdown("---")

        # Detalhes do time
        st.subheader("📋 Estatísticas Detalhadas")
        st.dataframe(df_time, width="stretch", hide_index=True)

    else:
        # Mostrar classificação completa
        st.subheader("📋 Classificação Geral")
        exibir_tabela_classificacao(df_classificacao)


elif menu == "👥 Elenco":
    st.title("👥 Elenco por Time")

    if time_selecionado:
        # Carregar dados
        elenco_use_case = get_elenco_use_case()
        df_elenco = elenco_use_case.execute()

        # Filtrar time específico
        df_time = df_elenco[
            df_elenco["Time"].str.contains(time_selecionado, case=False)
        ]

        st.subheader(f"👥 Elenco do {time_selecionado}")
        st.markdown(f"**Total de jogadores:** {len(df_time)}")

        # Estatísticas rápidas
        col1, col2, col3 = st.columns(3)

        with col1:
            posicoes = df_time["Posição"].value_counts()
            st.metric("Posições", len(posicoes))

        with col2:
            idades_validas = df_time["Idade"].dropna()
            if len(idades_validas) > 0:
                media_idade = float(idades_validas.mean())
                st.metric("Média de Idade", f"{media_idade:.1f} anos")
            else:
                st.metric("Média de Idade", "N/A")

        with col3:
            nacionalidades = df_time["NAC"].nunique()
            st.metric("Nacionalidades", nacionalidades)

        st.markdown("---")

        # Tabela de elenco
        exibir_tabela_elenco(df_time)
    else:
        st.info("👈 Selecione um time na barra lateral para ver o elenco.")
# ==============================================================================
# ESTILIZAÇÃO ADICIONAL PARA ELEMENTOS DO SIDEBAR
# ==============================================================================
st.markdown(
    """
    <style>
    /* Estilo para Radio Buttons e Selectbox na Sidebar */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        background: rgba(13, 40, 24, 0.5) !important;
        border-radius: 8px;
        padding: 8px;
    }
    
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] > div {
        background: rgba(13, 40, 24, 0.5) !important;
        border-radius: 8px;
    }
    
    /* Labels e textos da sidebar */
    [data-testid="stSidebar"] label {
        color: #00d4aa !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0 !important;
    }
    
    /* Títulos da sidebar */
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #00d4aa !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# ESTILIZAÇÃO DO HEADER (Topo)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Header / Top Bar */
    header[data-testid="stHeader"] {
        background: linear-gradient(90deg, #0d2818 0%, #061810 100%) !important;
        border-bottom: 1px solid rgba(0, 212, 170, 0.3);
    }
    
    /* Toolbar do header */
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    
    /* Botões do header */
    header button {
        color: #00d4aa !important;
    }
    
    /* Menu hamburger */
    [data-testid="stHamburger"] {
        color: #00d4aa !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# ESTILIZAÇÃO DOS CARDS DE MÉTRICAS
# ==============================================================================
st.markdown(
    """
    <style>
    /* Cards de métricas (st.metric) */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        border: 1px solid rgba(0, 212, 170, 0.15) !important;
        backdrop-filter: blur(8px);
    }
    
    /* Valor da métrica */
    [data-testid="stMetricValue"] {
        color: #00d4aa !important;
        font-weight: 600 !important;
    }
    
    /* Label da métrica */
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }
    
    /* Delta da métrica */
    [data-testid="stMetricDelta"] {
        color: #00ff88 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# ESTILIZAÇÃO DAS TABELAS (DataFrame)
# ==============================================================================
st.markdown(
    """
    <style>
    /* Container da tabela */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 212, 170, 0.1) !important;
    }
    
    /* Cabeçalho da tabela */
    [data-testid="stDataFrame"] thead th {
        background: rgba(13, 40, 24, 0.5) !important;
        color: #00d4aa !important;
        border-bottom: 1px solid rgba(0, 212, 170, 0.3) !important;
    }
    
    /* Linhas da tabela */
    [data-testid="stDataFrame"] tbody tr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(0, 212, 170, 0.05) !important;
    }
    
    /* Células da tabela */
    [data-testid="stDataFrame"] td {
        color: #e0e0e0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# ESTILIZAÇÃO DO MENU DE NAVEGAÇÃO
# ==============================================================================
st.markdown(
    """
    <style>
    /* Título da seção de navegação */
    [data-testid="stSidebar"] .stRadio > label {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: #00d4aa !important;
    }
    
    /* Itens do menu de navegação */
    [data-testid="stRadio"] div[role="radiogroup"] label {
        font-size: 16px !important;
        padding: 8px 12px !important;
        color: #e0e0e0 !important;
    }
    
    /* Hover nos itens do menu */
    [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: rgba(0, 212, 170, 0.1) !important;
        border-radius: 8px !important;
    }
    
    /* Item selecionado */
    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {
        background: rgba(0, 212, 170, 0.2) !important;
        border-radius: 8px !important;
        color: #00d4aa !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
