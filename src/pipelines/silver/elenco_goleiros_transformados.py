"""Pipeline Silver - Elenco Goleiros Transformados.

Tratamento e limpeza dos dados de goleiros extraídos da camada Bronze.
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
    """Executa o pipeline Silver de tratamento de goleiros."""
    console.print("\n[bold cyan]==============================================[/bold cyan]")
    console.print("[bold cyan]  GOLEIROS TRATADOS - CAMADA SILVER[/bold cyan]")
    console.print("[bold cyan]==============================================[/bold cyan]")
    console.print("[dim]Limpeza e tratamento de dados[/dim]\n")

    logger.info("=" * 60)
    logger.info("INICIANDO: Pipeline Silver - Tratamento de Goleiros")
    logger.info("=" * 60)

    # 1. Ler dados do Bronze
    bronze_path = settings.bronze_path / "elenco_goleiros.parquet"
    logger.info(f"Lendo dados de: {bronze_path}")

    if not bronze_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {bronze_path}")

    df = pd.read_parquet(bronze_path)
    logger.info(f"Dados lidos: {len(df)} registros")

    # Mostrar dados originais
    console.print("\n[bold yellow]DADOS ORIGINAIS (BRONZE):[/bold yellow]")
    console.print(f"Total de registros: [green]{len(df)}[/green]")

    # 2. Verificacao de dados Problematicos ANTES do tratamento
    console.print("\n[bold red]==============================================[/bold red]")
    console.print("[bold red]  VERIFICACAO ANTES DO TRATAMENTO[/bold red]")
    console.print("[bold red]==============================================[/bold red]")

    issues_before = check_data_quality(df)

    if issues_before:
        console.print("\n[yellow]Problemas encontrados:[/yellow]")

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

        # Mostrar registros com problemas
        console.print("\n[red]Registros com problemas:[/red]")

        has_problem = pd.Series([False] * len(df), index=df.index)
        for col in df.columns:
            has_problem = has_problem | df[col].isnull() | (df[col] == "") | (df[col] == "-") | (df[col] == "--")

        problem_rows = df[has_problem]

        problem_data_table = Table()
        problem_data_table.add_column("Nome", style="red")
        problem_data_table.add_column("Time", style="yellow")
        problem_data_table.add_column("POS", justify="center", style="red")
        problem_data_table.add_column("Idade", justify="center", style="red")
        problem_data_table.add_column("Alt", justify="center", style="red")
        problem_data_table.add_column("P", justify="center", style="red")
        problem_data_table.add_column("NAC", justify="center", style="red")
        problem_data_table.add_column("J", justify="center", style="red")
        problem_data_table.add_column("SUB", justify="center", style="red")
        problem_data_table.add_column("D", justify="center", style="red")
        problem_data_table.add_column("GS", justify="center", style="red")
        problem_data_table.add_column("A", justify="center", style="red")
        problem_data_table.add_column("FC", justify="center", style="red")
        problem_data_table.add_column("FS", justify="center", style="red")
        problem_data_table.add_column("CA", justify="center", style="red")
        problem_data_table.add_column("CV", justify="center", style="red")

        for _, row in problem_rows.iterrows():
            problem_data_table.add_row(
                str(row.get("Nome", "-")),
                str(row.get("Time", "-")),
                str(row.get("POS", "-")),
                str(row.get("Idade", "-")),
                str(row.get("Alt", "-")),
                str(row.get("P", "-")),
                str(row.get("NAC", "-")),
                str(row.get("J", "-")),
                str(row.get("SUB", "-")),
                str(row.get("D", "-")),
                str(row.get("GS", "-")),
                str(row.get("A", "-")),
                str(row.get("FC", "-")),
                str(row.get("FS", "-")),
                str(row.get("CA", "-")),
                str(row.get("CV", "-")),
            )

        console.print(problem_data_table)
        console.print(f"\n[red]Total de registros com problemas: {len(problem_rows)}[/red]")
    else:
        console.print("[green]Nenhum problema encontrado![/green]")

    # 3. Tratamento de dados
    console.print("\n[bold yellow]Aplicando tratamentos...[/bold yellow]")

    # Colunas numericas que devem ser substituidas por 0
    numeric_cols = ["POS", "Idade", "Alt", "P", "J", "SUB", "D", "GS", "A", "FC", "FS", "CA", "CV"]

    for col in numeric_cols:
        if col in df.columns:
            # Substituir valores nulos por 0
            df[col] = df[col].fillna(0)
            # Substituir strings vazias por 0
            df[col] = df[col].replace("", 0)
            # Substituir strings "-" e "--" por 0
            df[col] = df[col].replace("-", 0)
            df[col] = df[col].replace("--", 0)
            # Converter para numerico
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Colunas de texto - limpar caracteres especiais e ocultos
    text_cols = ["Nome", "Time", "NAC"]

    for col in text_cols:
        if col in df.columns:
            # Converter para string
            df[col] = df[col].astype(str)
            # Remover caracteres de controle (ocultos)
            df[col] = df[col].apply(lambda x: "".join(char for char in x if ord(char) >= 32 or char in "\n\t"))
            # Remover espacos extras
            df[col] = df[col].str.strip()
            # Substituir 'nan' por string vazia
            df[col] = df[col].replace("nan", "")
            # Substituir 'None' por string vazia
            df[col] = df[col].replace("None", "")

    logger.info("Tratamentos aplicados com sucesso!")

    # 4. Verificacao DEPOIS do tratamento
    console.print("\n[bold green]==============================================[/bold green]")
    console.print("[bold green]  VERIFICACAO DEPOIS DO TRATAMENTO[/bold green]")
    console.print("[bold green]==============================================[/bold green]")

    issues_after = check_data_quality(df)

    if issues_after:
        console.print("\n[yellow]Ainda existem problemas:[/yellow]")

        problem_table_after = Table()
        problem_table_after.add_column("Coluna", style="yellow")
        problem_table_after.add_column("Nulos", justify="center", style="red")
        problem_table_after.add_column("Vazios", justify="center", style="yellow")
        problem_table_after.add_column("Hifens (-)", justify="center", style="magenta")
        problem_table_after.add_column("Total", justify="center", style="bold red")

        for col, counts in issues_after.items():
            total = counts["nulos"] + counts["vazios"] + counts["hifens"]
            problem_table_after.add_row(
                col,
                str(counts["nulos"]),
                str(counts["vazios"]),
                str(counts["hifens"]),
                str(total),
            )

        console.print(problem_table_after)
    else:
        console.print("\n[bold green]✅ Todos os problemas foram corrigidos![/bold green]")
        console.print("[green]Nenhum dado nulo, vazio ou hifen encontrado apos o tratamento.[/green]")

    # 5. Mostrar dados TRATADOS/CORRIGIDOS
    console.print("\n[bold cyan]DADOS CORRIGIDOS (FINAL):[/bold cyan]")
    console.print(f"[green]Total de registros: {len(df)}[/green]")

    corrected_table = Table()
    corrected_table.add_column("Nome", style="green")
    corrected_table.add_column("Time", style="yellow")
    corrected_table.add_column("POS", justify="center", style="cyan")
    corrected_table.add_column("Idade", justify="center", style="cyan")
    corrected_table.add_column("Alt", justify="center", style="cyan")
    corrected_table.add_column("P", justify="center", style="cyan")
    corrected_table.add_column("NAC", justify="center", style="cyan")
    corrected_table.add_column("J", justify="center", style="cyan")
    corrected_table.add_column("SUB", justify="center", style="cyan")
    corrected_table.add_column("D", justify="center", style="cyan")
    corrected_table.add_column("GS", justify="center", style="cyan")
    corrected_table.add_column("A", justify="center", style="cyan")
    corrected_table.add_column("FC", justify="center", style="cyan")
    corrected_table.add_column("FS", justify="center", style="cyan")
    corrected_table.add_column("CA", justify="center", style="cyan")
    corrected_table.add_column("CV", justify="center", style="cyan")

    for _, row in df.iterrows():
        corrected_table.add_row(
            str(row.get("Nome", "-")),
            str(row.get("Time", "-")),
            str(row.get("POS", "-")),
            str(row.get("Idade", "-")),
            str(row.get("Alt", "-")),
            str(row.get("P", "-")),
            str(row.get("NAC", "-")),
            str(row.get("J", "-")),
            str(row.get("SUB", "-")),
            str(row.get("D", "-")),
            str(row.get("GS", "-")),
            str(row.get("A", "-")),
            str(row.get("FC", "-")),
            str(row.get("FS", "-")),
            str(row.get("CA", "-")),
            str(row.get("CV", "-")),
        )

    console.print(corrected_table)

    # 6. Salvar dados no Silver
    silver_path = settings.silver_path / "elenco_goleiros_tratados.parquet"
    df.to_parquet(silver_path, index=False)
    logger.info(f"Dados salvos em: {silver_path}")

    console.print("\n[bold green]==============================================[/bold green]")
    console.print("[bold green]  Pipeline Silver Concluido[/bold green]")
    console.print(f"Total de goleiros: [green]{len(df)}[/green]")
    console.print(f"Arquivo salvo em: [cyan]{silver_path}[/cyan]")
    console.print("[bold green]==============================================[/bold green]\n")

    return silver_path


if __name__ == "__main__":
    run()
