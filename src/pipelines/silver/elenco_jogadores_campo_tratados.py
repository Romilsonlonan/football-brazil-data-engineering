"""Pipeline Silver - Elenco Jogadores de Campo Transformados.

Tratamento e limpeza dos dados de jogadores de campo extraidos da camada Bronze.
"""

import pandas as pd
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.configs import settings
from src.utils.logger import logger


console = Console(force_terminal=True, file=sys.stdout)


def check_data_quality(df: pd.DataFrame) -> dict:
    """Verifica qualidade dos dados: nulos, vazios, e '--'."""
    issues = {}

    for col in df.columns:
        null_count = df[col].isnull().sum()
        empty_count = (df[col] == "").sum() if df[col].dtype == object else 0
        dash_count = ((df[col] == "-") | (df[col] == "--")).sum()

        if null_count > 0 or empty_count > 0 or dash_count > 0:
            issues[col] = {
                "nulos": null_count,
                "vazios": empty_count,
                "hifens": dash_count,
            }

    return issues


def run():
    """Executa o pipeline Silver de tratamento de jogadores de campo."""
    console.print("\n[bold cyan]==============================================[/bold cyan]")
    console.print("[bold cyan]  JOGADORES DE CAMPO - CAMADA SILVER[/bold cyan]")
    console.print("[bold cyan]==============================================[/bold cyan]")
    console.print("[dim]Limpeza e tratamento de dados[/dim]\n")

    logger.info("=" * 60)
    logger.info("INICIANDO: Pipeline Silver - Tratamento de Jogadores de Campo")
    logger.info("=" * 60)

    # 1. Ler dados do Bronze
    bronze_path = settings.bronze_path / "elenco_jogadores_campo.parquet"
    logger.info(f"Lendo dados de: {bronze_path}")

    if not bronze_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {bronze_path}")

    df_original = pd.read_parquet(bronze_path)
    logger.info(f"Dados lidos: {len(df_original)} registros")

    # Criar copia para trabalhar
    df = df_original.copy()

    # Mostrar dados originais
    console.print("\n[bold yellow]DADOS ORIGINAIS (BRONZE):[/bold yellow]")
    console.print(f"Total de registros: [green]{len(df)}[/green]")

    # 2. Verificacao de dados Problematicos ANTES do tratamento
    console.print("\n[bold red]==============================================[/bold red]")
    console.print("[bold red]  VERIFICACAO ANTES DO TRATAMENTO[/bold red]")
    console.print("[bold red]==============================================[/bold red]")

    issues_before = check_data_quality(df)

    # Identificar registros com problemas ANTES do tratamento
    has_problem = pd.Series([False] * len(df), index=df.index)
    for col in df.columns:
        has_problem = has_problem | df[col].isnull() | (df[col] == "") | (df[col] == "-") | (df[col] == "--")

    problem_rows_before = df[has_problem].copy()
    problem_indices = problem_rows_before.index.tolist()

    if issues_before:
        console.print("\n[yellow]Resumo - Colunas com problemas:[/yellow]")

        problem_table = Table()
        problem_table.add_column("Coluna", style="yellow")
        problem_table.add_column("Nulos", justify="center", style="red")
        problem_table.add_column("Vazios", justify="center", style="yellow")
        problem_table.add_column("Hifens (-)", justify="center", style="magenta")
        problem_table.add_column("Total", justify="center", style="bold red")

        for col, counts in issues_before.items():
            total = counts["nulos"] + counts["vazios"] + counts["hifens"]
            problem_table.add_row(
                col,
                str(counts["nulos"]),
                str(counts["vazios"]),
                str(counts["hifens"]),
                str(total),
            )

        console.print(problem_table)
        console.print(f"\n[red]Total de registros com problemas: {len(problem_rows_before)}[/red]")
    else:
        console.print("[green]Nenhum problema encontrado![/green]")

    # 3. Tratamento de dados
    console.print("\n[bold yellow]Aplicando tratamentos...[/bold yellow]")

    # Colunas numericas que devem ser substituidas por 0
    numeric_cols = ["POS", "Idade", "Alt", "P", "J", "SUB", "G", "A", "TC", "CG", "FC", "FS", "CA", "CV"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            df[col] = df[col].replace("", 0)
            df[col] = df[col].replace("-", 0)
            df[col] = df[col].replace("--", 0)
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Colunas de texto - limpar caracteres especiais e ocultos
    text_cols = ["Nome", "Time", "NAC"]

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(lambda x: "".join(char for char in x if ord(char) >= 32 or char in "\n\t"))
            df[col] = df[col].str.strip()
            df[col] = df[col].replace("nan", "")
            df[col] = df[col].replace("None", "")

    logger.info("Tratamentos aplicados com sucesso!")

    # 4. Verificacao DEPOIS do tratamento
    console.print("\n[bold green]==============================================[/bold green]")
    console.print("[bold green]  VERIFICACAO DEPOIS DO TRATAMENTO[/bold green]")
    console.print("[bold green]==============================================[/bold green]")

    issues_after = check_data_quality(df)

    if issues_after:
        console.print("\n[yellow]Ainda existem problemas:[/yellow]")
        for col, counts in issues_after.items():
            console.print(f"  {col}: {counts['nulos']} nulos, {counts['vazios']} vazios, {counts['hifens']} hifens")
    else:
        console.print("\n[bold green]✅ Todos os problemas foram corrigidos![/bold green]")
        console.print("[green]Nenhum dado nulo, vazio ou hifen encontrado.[/green]")

    # 5. Mostrar ANTES e DEPOIS das mesmas linhas corrigidas
    if len(problem_indices) > 0:
        console.print("\n[bold magenta]==============================================[/bold magenta]")
        console.print("[bold magenta]  ANTES E DEPOIS - LINHAS CORRIGIDAS[/bold magenta]")
        console.print("[bold magenta]==============================================[/bold magenta]")

        console.print("\n[red]ANTES (com problemas):[/red]")
        console.print("[yellow]OBS: Valores com '--', '-', vazio ou nulo serao mostrados[/yellow]")

        before_table = Table()
        before_table.add_column("Nome", style="red")
        before_table.add_column("Time", style="yellow")
        before_table.add_column("POS", justify="center", style="red")
        before_table.add_column("Idade", justify="center", style="red")
        before_table.add_column("J", justify="center", style="red")
        before_table.add_column("G", justify="center", style="red")
        before_table.add_column("A", justify="center", style="red")
        before_table.add_column("TC", justify="center", style="red")
        before_table.add_column("FC", justify="center", style="red")

        # Mostrar linhas problematicas ANTES (do DataFrame original)
        for idx in problem_indices[:10]:
            row = df_original.loc[idx]
            before_table.add_row(
                str(row.get("Nome", "-")),
                str(row.get("Time", "-")),
                str(row.get("POS", "-")),
                str(row.get("Idade", "-")),
                str(row.get("J", "-")),
                str(row.get("G", "-")),
                str(row.get("A", "-")),
                str(row.get("TC", "-")),
                str(row.get("FC", "-")),
            )

        console.print(before_table)

        console.print("\n[green]DEPOIS (corrigidos):[/green]")
        console.print("[cyan]OBS: Valores '--', '-', vazio ou nulo foram substituidos por 0[/cyan]")

        after_table = Table()
        after_table.add_column("Nome", style="green")
        after_table.add_column("Time", style="yellow")
        after_table.add_column("POS", justify="center", style="green")
        after_table.add_column("Idade", justify="center", style="green")
        after_table.add_column("J", justify="center", style="green")
        after_table.add_column("G", justify="center", style="green")
        after_table.add_column("A", justify="center", style="green")
        after_table.add_column("TC", justify="center", style="green")
        after_table.add_column("FC", justify="center", style="green")

        # Mostrar as mesmas linhas DEPOIS (agora corrigidas)
        for idx in problem_indices[:10]:
            row = df.loc[idx]
            after_table.add_row(
                str(row.get("Nome", "-")),
                str(row.get("Time", "-")),
                str(row.get("POS", "-")),
                str(row.get("Idade", "-")),
                str(row.get("J", "-")),
                str(row.get("G", "-")),
                str(row.get("A", "-")),
                str(row.get("TC", "-")),
                str(row.get("FC", "-")),
            )

        console.print(after_table)
    else:
        console.print("\n[green]Nenhuma linha necessitou correção![/green]")

    # 6. Mostrar todos os dados tratados
    console.print("\n[bold cyan]DADOS FINAIS (TRATADOS):[/bold cyan]")
    console.print(f"[green]Total de registros: {len(df)}[/green]")

    final_table = Table()
    final_table.add_column("Nome", style="green")
    final_table.add_column("Time", style="yellow")
    final_table.add_column("POS", justify="center", style="cyan")
    final_table.add_column("Idade", justify="center", style="cyan")
    final_table.add_column("J", justify="center", style="cyan")
    final_table.add_column("G", justify="center", style="cyan")
    final_table.add_column("A", justify="center", style="cyan")

    for _, row in df.head(10).iterrows():
        final_table.add_row(
            str(row.get("Nome", "-")),
            str(row.get("Time", "-")),
            str(row.get("POS", "-")),
            str(row.get("Idade", "-")),
            str(row.get("J", "-")),
            str(row.get("G", "-")),
            str(row.get("A", "-")),
        )

    console.print(final_table)

    # 7. Salvar dados no Silver
    silver_path = settings.silver_path / "elenco_jogadores_campo_tratados.parquet"
    df.to_parquet(silver_path, index=False)
    logger.info(f"Dados salvos em: {silver_path}")

    console.print("\n[bold green]==============================================[/bold green]")
    console.print("[bold green]  Pipeline Silver Concluido[/bold green]")
    console.print(f"Total de jogadores: [green]{len(df)}[/green]")
    console.print(f"Arquivo salvo em: [cyan]{silver_path}[/cyan]")
    console.print("[bold green]==============================================[/bold green]\n")

    return silver_path


if __name__ == "__main__":
    run()
