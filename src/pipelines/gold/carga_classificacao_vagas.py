"""Pipeline Gold - Carga de Classificação com Vagas.
=======================================================

Este pipeline é responsável por:
- Ler os dados da camada Silver (dados tratados)
- Calcular as vagas para Libertadores, Sul-Americana e Rebaixamento
- Salvar os dados com a coluna de zona/vaga

Fluxo:
    Silver (Tratado) → Gold Vagas (Com zonas)

Tags: gold, vagas, classificacao, libertadores, sul-americana
"""

import logging

import pandas as pd
from sqlalchemy import create_engine, text

from src.configs import settings
from rich.console import Console
from rich.table import Table

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
console = Console()


def get_zona_brasileirao(posicao: int, campeao_copa_brasil: bool = False) -> str:
    """
    Retorna a zona/vaga do time baseado na posição no Brasileirão.

    Regras:
    - 1º-4º: Libertadores (G4)
    - 5º: Pré-Libertadores (G5) - apenas se não houver campeão da Copa do Brasil no G4
    - 6º: Libertadores (G6)
    - 7º-12º: Sul-Americana
    - 13º-16º: Sem vaga
    - 17º-20º: Rebaixamento

    Args:
        posicao: Posição do time na tabela (1-20)
        campeao_copa_brasil: Se o campeão da Copa do Brasil estiver no G4

    Returns:
        String com a zona do time
    """
    if posicao <= 4:
        return "LIBERTADORES (G4)"
    elif posicao == 5 and not campeao_copa_brasil:
        return "PRÉ-LIBERTADORES (G5)"
    elif posicao == 5 and campeao_copa_brasil:
        return "LIBERTADORES (G5)"
    elif posicao == 6:
        return "LIBERTADORES (G6)"
    elif 7 <= posicao <= 12:
        return "SUL-AMERICANA"
    elif 13 <= posicao <= 16:
        return "SEM VAGA"
    elif 17 <= posicao <= 20:
        return "REBAIXAMENTO"
    else:
        return "INVÁLIDO"


def get_status_curto(posicao: int) -> str:
    """Retorna status curto para display."""
    if posicao <= 4:
        return "LIB"
    elif posicao == 5:
        return "PRE-LIB"
    elif posicao == 6:
        return "LIB"
    elif 7 <= posicao <= 12:
        return "SUL-AM"
    elif 13 <= posicao <= 16:
        return "SEM_VAGA"
    elif 17 <= posicao <= 20:
        return "REBAIX"
    else:
        return "INV"


def run():
    """Executa o pipeline Gold de classificação com vagas."""
    logger.info("=" * 60)
    logger.info("🔄 PIPELINE GOLD - CLASSIFICAÇÃO COM VAGAS")
    logger.info("Calculando zonas de classificação")
    logger.info("=" * 60)

    # Caminho do arquivo Silver
    silver_path = settings.silver_path / "classificacao-limpa.parquet"

    if not silver_path.exists():
        raise FileNotFoundError(f"Arquivo Silver não encontrado: {silver_path}")

    logger.info(f"Lendo dados de: {silver_path}")

    # Ler arquivo Parquet
    df = pd.read_parquet(silver_path)

    if df.empty:
        raise ValueError("DataFrame está vazio. Não há dados para processar.")

    logger.info(f"Arquivo lido: {len(df)} registros, {len(df.columns)} colunas")
    logger.info(f"Colunas originais: {df.columns.tolist()}")

    # ============================================
    # Calcular vagas/zonas
    # ============================================
    logger.info("")
    logger.info("🎯 ETAPA 1: Calculando zonas de classificação...")

    # Adicionar coluna de zona (sem campeão da Copa do Brasil por padrão)
    df["zona"] = df["posicao"].apply(
        lambda x: get_zona_brasileirao(x, campeao_copa_brasil=False)
    )
    df["status_curto"] = df["posicao"].apply(get_status_curto)

    # Adicionar coluna de aproveitamento
    df["aproveitamento"] = df.apply(
        lambda row: (
            round((row["pontos"] / (row["jogos"] * 3)) * 100, 2)
            if row["jogos"] > 0
            else 0.0
        ),
        axis=1,
    )

    logger.info(f"✅ Zonas calculadas para {len(df)} times")

    # Exibir tabela com vagas
    console.print("")
    console.print("[bold cyan]📊 CLASSIFICAÇÃO BRASILEIRÃO - COM VAGAS[/bold cyan]")

    # Criar tabela Rich
    table = Table(
        title="[bold green]Classificação Brasileirão - Vagas[/bold green]",
        show_header=True,
        header_style="bold magenta",
    )

    # Adicionar colunas
    table.add_column("Posição", justify="center", style="cyan")
    table.add_column("Time", style="green")
    table.add_column("Pontos", justify="center", style="yellow")
    table.add_column("Jogos", justify="center")
    table.add_column("Vitórias", justify="center", style="green")
    table.add_column("Empates", justify="center", style="yellow")
    table.add_column("Derrotas", justify="center", style="red")
    table.add_column("Gols Pro", justify="center")
    table.add_column("Gols Contra", justify="center")
    table.add_column("Saldo", justify="center")
    table.add_column("Zona", style="bold white")

    # Adicionar linhas
    for _, row in df.sort_values("posicao").iterrows():
        posicao = row["posicao"]

        # Determinar cor baseada na zona
        if "LIBERTADORES" in row["zona"]:
            style = "bold green"
        elif "SUL-AMERICANA" in row["zona"]:
            style = "bold blue"
        elif "REBAIXAMENTO" in row["zona"]:
            style = "bold red"
        else:
            style = "white"

        table.add_row(
            str(posicao),
            row["time"][:20],
            str(row["pontos"]),
            str(row["jogos"]),
            str(row["vitorias"]),
            str(row["empates"]),
            str(row["derrotas"]),
            str(row["gols_pro"]),
            str(row["gols_contra"]),
            str(row["saldo_gols"]),
            f"[{style}]{row['zona']}[/{style}]",
        )

    console.print(table)

    # Exibir resumo das vagas
    console.print("\n")
    vagas_table = Table(
        title="🎯 RESUMO DAS VAGAS", show_header=True, header_style="bold cyan"
    )
    vagas_table.add_column("Competição", style="yellow")
    vagas_table.add_column("Posições", style="white")
    vagas_table.add_column("Times", style="green")

    lib_count = len(df[df["zona"].str.contains("LIBERTADORES")])
    sul_count = len(df[df["zona"].str.contains("SUL-AMERICANA")])
    reb_count = len(df[df["zona"].str.contains("REBAIXAMENTO")])

    vagas_table.add_row("🟢 Libertadores", "1º ao 6º lugar", str(lib_count))
    vagas_table.add_row("🔵 Sul-Americana", "7º ao 12º lugar", str(sul_count))
    vagas_table.add_row("🔴 Rebaixamento", "17º ao 20º lugar", str(reb_count))

    console.print(vagas_table)

    # ============================================
    # Salvar arquivo Parquet na Gold
    # ============================================
    logger.info("")
    logger.info("💾 ETAPA 2: Salvando arquivo Parquet na Gold...")

    gold_path = settings.gold_path / "classificacao-vagas.parquet"
    gold_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(gold_path, index=False)
    logger.info(f"✅ Arquivo Parquet salvo em: {gold_path}")

    if settings.minio_enabled:
        from src.utils.minio_client import save_to_minio

        minio_path = save_to_minio(df, "gold", "classificacao-vagas.parquet")
        if minio_path:
            logger.info(f"☁️  Arquivo Parquet salvo no MinIO: {minio_path}")
        else:
            logger.warning("⚠️  Falha ao salvar no MinIO")

    # ============================================
    # Carregar para PostgreSQL (se disponível)
    # ============================================
    logger.info("")
    logger.info("💽 ETAPA 3: Carregando dados para PostgreSQL...")

    # Conectar ao PostgreSQL
    postgres_user = settings.postgres_user
    postgres_password = settings.postgres_password
    postgres_host = settings.postgres_host
    postgres_port = str(settings.postgres_port)
    postgres_db = settings.postgres_db

    # Validar credenciais
    if (
        not postgres_user
        or not postgres_password
        or not postgres_host
        or not postgres_db
        or settings.postgres_port == 0
    ):
        logger.warning(
            "⚠️ Configurações do PostgreSQL não encontradas. Pulando etapa de carga no banco."
        )
        logger.info("=" * 60)
        logger.info("✅ PIPELINE GOLD VAGAS - CONCLUÍDO (APENAS PARQUET)")
        logger.info(f"   Arquivo salvo em: {gold_path}")
        logger.info("=" * 60)
        return {
            "rows_inserted": len(df),
            "file_path": str(gold_path),
            "status": "PARQUET_ONLY",
        }

    conn_string = f"postgresql+psycopg2://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    logger.info(
        f"Conectando ao PostgreSQL em {postgres_host}:{postgres_port}/{postgres_db}"
    )

    engine = create_engine(conn_string)

    # Testar conexão
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"Conexão estabelecida: {version[:50]}...")
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível conectar ao PostgreSQL: {e}")
        logger.info("   Pulando etapa de carga no banco.")
        logger.info("=" * 60)
        logger.info("✅ PIPELINE GOLD VAGAS - CONCLUÍDO (APENAS PARQUET)")
        logger.info(f"   Arquivo salvo em: {gold_path}")
        logger.info("=" * 60)
        return {
            "rows_inserted": len(df),
            "file_path": str(gold_path),
            "status": "PARQUET_ONLY",
        }

    # Inserir dados
    table_name = "gold_classificacao_vagas"
    schema_name = "public"

    logger.info(f"Inserindo dados na tabela: {schema_name}.{table_name}")

    df.to_sql(table_name, engine, schema=schema_name, if_exists="replace", index=False)

    logger.info(
        f"✅ Sucesso! {len(df)} registros inseridos na tabela '{schema_name}.{table_name}'"
    )

    logger.info("=" * 60)
    logger.info("✅ PIPELINE GOLD VAGAS - CONCLUÍDO!")
    logger.info(f"   Registros: {len(df)}")
    logger.info(f"   Arquivo: {gold_path}")
    logger.info(f"   Tabela: {schema_name}.{table_name}")
    logger.info("=" * 60)

    return {
        "rows_inserted": len(df),
        "table_name": table_name,
        "file_path": str(gold_path),
        "status": "SUCCESS",
    }


if __name__ == "__main__":
    run()
