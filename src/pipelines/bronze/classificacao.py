"""Pipeline Bronze - Classificacao."""

from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

from src.pipelines.bronze.base import BasePipeline
from src.configs import settings
from src.utils.logger import logger

console = Console()


class ClassificacaoBronzePipeline(BasePipeline):
    """
    Pipeline Bronze para dados de classificação do Brasileirão.

    Este pipeline é responsável por:
    - Extrair dados de classificação (rankings, pontuações)
    - Armazenar os dados brutos na camada Bronze
    """

    def __init__(self):
        super().__init__("bronze_classificacao")
        logger.info("Pipeline Bronze Classificacao inicializado")
        logger.warning(
            "bronze_classificacao:bronze - Este pipeline faz apenas extração para visualização"
        )

    def extract(self, **kwargs) -> pd.DataFrame:
        """Extrai dados da fonte (scraper ESPN com Playwright)."""
        logger.info("Extraindo dados de classificação...")

        url = "https://www.espn.com.br/futebol/classificacao/_/liga/bra.1/temporada/2026"

        try:
            logger.info("📊 CLASSIFICACAO BRASILEIRAO 2026 - Dados extraidos da ESPN")

            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=30000)

                html = page.content()
                logger.info(f"Página carregada - HTML: {len(html)} chars")

                browser.close()

            soup = BeautifulSoup(html, "html.parser")

            tabela_nomes = soup.select_one("div.Table__Scroller--fixed table")
            tabela_stats = soup.select_one("div.Table__Scroller table")

            # ✅ FIX: sem lambda no find_all — filtra por list comprehension
            if not tabela_nomes or not tabela_stats:
                todas_tabelas = soup.find_all("table")
                tabelas = [
                    t for t in todas_tabelas
                    if "Table" in " ".join(list(t.get("class") or []))
                ]
                logger.warning(f"Encontradas {len(tabelas)} tabelas no fallback")

                if len(tabelas) >= 2:
                    tabela_nomes = tabelas[0]
                    tabela_stats = tabelas[1]
                else:
                    logger.error("Tabelas não encontradas no HTML da página!")
                    return pd.DataFrame()

            # ✅ FIX: sem anotações Tag — Python infere corretamente
            linhas_nomes = list(tabela_nomes.select("tbody tr"))
            linhas_stats = list(tabela_stats.select("tbody tr"))

            logger.info(f"Times encontrados: {len(linhas_nomes)}")

            dados = []
            for i in range(min(len(linhas_nomes), len(linhas_stats))):
                linha_nome = linhas_nomes[i]
                linha_stat = linhas_stats[i]

                col_nome = linha_nome.find_all("td")
                col_stat = linha_stat.find_all("td")

                if len(col_nome) < 1 or len(col_stat) < 8:
                    continue

                # ✅ FIX: sem anotação Tag no nome_element
                nome_element = (
                    col_nome[0].select_one(".hide-mobile")
                    or col_nome[0].select_one("a")
                    or col_nome[0].select_one("span")
                    or col_nome[0]
                )
                time = nome_element.get_text(strip=True)

                if not time:
                    continue

                def safe_int(col, idx: int) -> int:
                    """Converte célula para int com fallback 0."""
                    val = col[idx].get_text(strip=True) if len(col) > idx else "0"
                    return int(val) if val.lstrip("+-").isdigit() else 0

                dados.append({
                    "Posição": i + 1,
                    "Time":    time,
                    "J":       safe_int(col_stat, 0),
                    "V":       safe_int(col_stat, 1),
                    "E":       safe_int(col_stat, 2),
                    "D":       safe_int(col_stat, 3),
                    "GP":      safe_int(col_stat, 4),
                    "GC":      safe_int(col_stat, 5),
                    "SG":      safe_int(col_stat, 6),
                    "PTS":     safe_int(col_stat, 7),
                })

            df = pd.DataFrame(dados)

            # ── Exibição com Rich ─────────────────────────────────────────────
            table = Table(
                title="[bold green]📊 CLASSIFICAÇÃO BRASILEIRÃO 2026 - DADOS CRUS (BRONZE)[/bold green]",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Pos", style="cyan",        justify="center", width=4)
            table.add_column("Time",style="green",                         width=20)
            table.add_column("J",   style="white",       justify="center", width=3)
            table.add_column("V",   style="yellow",      justify="center", width=3)
            table.add_column("E",   style="blue",        justify="center", width=3)
            table.add_column("D",   style="red",         justify="center", width=3)
            table.add_column("GP",  style="white",       justify="center", width=4)
            table.add_column("GC",  style="white",       justify="center", width=4)
            table.add_column("SG",  style="white",       justify="center", width=4)
            table.add_column("PTS", style="bold yellow", justify="center", width=5)

            for _, row in df.iterrows():
                if row["Posição"] <= 4:
                    pos_style = "bold green"   # Libertadores
                elif row["Posição"] <= 12:
                    pos_style = "bold cyan"    # Sul-americana
                elif row["Posição"] >= 17:
                    pos_style = "bold red"     # Rebaixamento
                else:
                    pos_style = "white"

                table.add_row(
                    f"[{pos_style}]{row['Posição']}[/{pos_style}]",
                    row["Time"][:20],
                    str(row["J"]),
                    str(row["V"]),
                    str(row["E"]),
                    str(row["D"]),
                    str(row["GP"]),
                    str(row["GC"]),
                    f"{row['SG']:+d}",
                    str(row["PTS"]),
                )

            console.print(table)
            console.print(f"[bold]Total:[/bold] [cyan]{len(df)}[/cyan] times (dados brutos)")

            return df

        except Exception as e:
            logger.error(f"Erro ao extrair classificação: {e}")
            return pd.DataFrame()

    def transform(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transforma os dados — Bronze não aplica transformações."""
        logger.info("Transform: passando dados direto (sem transformação no Bronze)")
        return df

    def load(self, df: pd.DataFrame, table_name: str = "classificacao", **kwargs) -> Path:
        """Carrega os dados na camada Bronze."""
        if df.empty:
            logger.warning("DataFrame vazio — nada para salvar!")
            return Path()

        output_path = settings.bronze_path / f"{table_name}.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        logger.info(f"Dados salvos em: {output_path}")
        return output_path

    def run(self, **kwargs) -> Path:
        """Executa o pipeline completo (Extract → Transform → Load)."""
        logger.info("=" * 60)
        logger.info("INICIANDO PIPELINE BRONZE - CLASSIFICACAO")
        logger.info("=" * 60)

        try:
            df = self.extract(**kwargs)
            df = self.transform(df, **kwargs)
            output_path = self.load(df, **kwargs)

            logger.info("=" * 60)
            logger.info("PIPELINE BRONZE - CLASSIFICACAO CONCLUIDO")
            logger.info("=" * 60)

            return output_path

        except Exception as e:
            logger.error(f"Pipeline falhou: {e}")
            raise


def run():
    """Função de entrada."""
    pipeline = ClassificacaoBronzePipeline()
    pipeline.run()


if __name__ == "__main__":
    run()