"""Pipeline Bronze - Classificacao."""

from pathlib import Path

import pandas as pd
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
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/120.0.0.0 Safari/537.36"
            )
        }
        logger.info("Pipeline Bronze Classificacao inicializado")
        logger.warning(
            " bronze_classificacao:bronze - Este pipeline faz apenas extração para visualização"
        )

    def extract(self, **kwargs) -> pd.DataFrame:
        """Extrai dados da fonte (scraper ESPN)."""
        logger.info("Extraindo dados de classificação...")

        import requests
        from bs4 import BeautifulSoup

        url = (
            "https://www.espn.com.br/futebol/classificacao/_/liga/bra.1/temporada/2026"
        )

        try:
            logger.info("📊 CLASSIFICACAO BRASILEIRAO 2026 - Dados extraidos da ESPN")

            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info(f"Resposta: {response.status_code}")

            soup = BeautifulSoup(response.content, "html.parser")

            # Encontrar tabelas
            tabela_nomes = soup.select_one("div.Table__Scroller--fixed table")
            tabela_stats = soup.select_one("div.Table__Scroller table")

            if not tabela_nomes or not tabela_stats:
                tabelas = soup.find_all("table", class_=lambda x: x and "Table" in x)
                if len(tabelas) >= 2:
                    tabela_nomes = tabelas[0]
                    tabela_stats = tabelas[1]
                else:
                    logger.warning("Tabelas não encontradas no HTML da página")
                    logger.error("Tabelas não encontradas!")
                    return pd.DataFrame()

            linhas_nomes = tabela_nomes.select("tbody tr")
            linhas_stats = tabela_stats.select("tbody tr")

            logger.info(f"Times encontrados: {len(linhas_nomes)}")

            # Processar dados
            dados = []
            for i in range(min(len(linhas_nomes), len(linhas_stats))):
                col_nome = linhas_nomes[i].find_all("td")
                col_stat = linhas_stats[i].find_all("td")

                if len(col_nome) < 1 or len(col_stat) < 8:
                    continue

                # Nome do time
                nome_element = (
                    col_nome[0].select_one(".hide-mobile")
                    or col_nome[0].select_one("a")
                    or col_nome[0].select_one("span")
                    or col_nome[0]
                )
                time = nome_element.get_text(strip=True)

                if not time:
                    continue

                # Estatísticas
                jogos = col_stat[0].get_text(strip=True) if len(col_stat) > 0 else "0"
                vitorias = (
                    col_stat[1].get_text(strip=True) if len(col_stat) > 1 else "0"
                )
                empates = col_stat[2].get_text(strip=True) if len(col_stat) > 2 else "0"
                derrotas = (
                    col_stat[3].get_text(strip=True) if len(col_stat) > 3 else "0"
                )
                gp = col_stat[4].get_text(strip=True) if len(col_stat) > 4 else "0"
                gc = col_stat[5].get_text(strip=True) if len(col_stat) > 5 else "0"
                sg = col_stat[6].get_text(strip=True) if len(col_stat) > 6 else "0"
                pts = col_stat[7].get_text(strip=True) if len(col_stat) > 7 else "0"

                dados.append(
                    {
                        "Posição": i + 1,
                        "Time": time,
                        "J": int(jogos) if jogos.isdigit() else 0,
                        "V": int(vitorias) if vitorias.isdigit() else 0,
                        "E": int(empates) if empates.isdigit() else 0,
                        "D": int(derrotas) if derrotas.isdigit() else 0,
                        "GP": int(gp) if gp.isdigit() else 0,
                        "GC": int(gc) if gc.isdigit() else 0,
                        "SG": int(sg) if sg.lstrip("+-").isdigit() else 0,
                        "PTS": int(pts) if pts.isdigit() else 0,
                    }
                )

            df = pd.DataFrame(dados)

            # Mostrar tabela com Rich
            table = Table(
                title="[bold green]📊 CLASSIFICAÇÃO BRASILEIRÃO 2026 - DADOS CRUS (BRONZE)[/bold green]",
                show_header=True,
                header_style="bold magenta",
            )

            # Adicionar colunas
            table.add_column("Pos", style="cyan", justify="center", width=4)
            table.add_column("Time", style="green", width=20)
            table.add_column("J", style="white", justify="center", width=3)
            table.add_column("V", style="yellow", justify="center", width=3)
            table.add_column("E", style="blue", justify="center", width=3)
            table.add_column("D", style="red", justify="center", width=3)
            table.add_column("GP", style="white", justify="center", width=4)
            table.add_column("GC", style="white", justify="center", width=4)
            table.add_column("SG", style="white", justify="center", width=4)
            table.add_column("PTS", style="bold yellow", justify="center", width=5)

            # Adicionar linhas
            for _, row in df.iterrows():
                # Colorir posições especiais
                if row["Posição"] <= 4:
                    pos_style = "bold green"  # Libertadores
                elif row["Posição"] <= 12:
                    pos_style = "bold cyan"  # Sul-americana
                elif row["Posição"] >= 17:
                    pos_style = "bold red"  # Rebaixados
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
            console.print(
                f"[bold]Total:[/bold] [cyan]{len(df)}[/cyan] times (dados brutos)"
            )

            return df

        except Exception as e:
            logger.error(f"Erro ao extrair classificação: {e}")
            logger.warning("Retornando DataFrame vazio devido ao erro")
            logger.error(f"Erro: {e}")
            return pd.DataFrame()

    def transform(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transforma os dados (limpeza básica)."""
        logger.info("Transformando dados de classificação...")
        logger.warning(
            "Transformação não implementada - passando dados direto para load"
        )
        return df

    def load(
        self, df: pd.DataFrame, table_name: str = "classificacao", **kwargs
    ) -> Path:
        """Carrega os dados na camada Bronze."""
        output_path = settings.bronze_path / f"{table_name}.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        logger.info(f"Dados salvos em: {output_path}")
        return output_path

    def run(self, **kwargs) -> Path:
        """Executa o pipeline completo."""
        logger.info("=" * 60)
        logger.info("INICIANDO PIPELINE BRONZE - CLASSIFICACAO")
        logger.info("=" * 60)

        try:
            # Extract
            df = self.extract(**kwargs)

            # Transform
            df = self.transform(df, **kwargs)

            # Load
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
