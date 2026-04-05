"""Pipeline Bronze - Elenco Goleiros.

Extração de dados brutos dos goleiros dos 20 times do Brasileirão 2026.
Fonte: ESPN (web scraping)
"""

from pathlib import Path
import sys
import time
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich import box

from src.pipelines.bronze.base import BasePipeline
from src.configs import settings
from src.utils.logger import logger


# URLs dos times do Brasileirão 2026
TEAMS_URLS = {
    "Athletico-PR": "https://www.espn.com.br/futebol/time/elenco/_/id/3458",
    "Atlético-MG": "https://www.espn.com.br/futebol/time/elenco/_/id/7632",
    "Bahia": "https://www.espn.com.br/futebol/time/elenco/_/id/9967",
    "Botafogo": "https://www.espn.com.br/futebol/time/elenco/_/id/6086",
    "Chapecoense": "https://www.espn.com.br/futebol/time/elenco/_/id/9318",
    "Corinthians": "https://www.espn.com.br/futebol/time/elenco/_/id/874",
    "Coritiba": "https://www.espn.com.br/futebol/time/elenco/_/id/3456",
    "Cruzeiro": "https://www.espn.com.br/futebol/time/elenco/_/id/2022",
    "Flamengo": "https://www.espn.com.br/futebol/time/elenco/_/id/819",
    "Fluminense": "https://www.espn.com.br/futebol/time/elenco/_/id/3445",
    "Grêmio": "https://www.espn.com.br/futebol/time/elenco/_/id/6273",
    "Internacional": "https://www.espn.com.br/futebol/time/elenco/_/id/1936",
    "Mirassol": "https://www.espn.com.br/futebol/time/elenco/_/id/9169",
    "Palmeiras": "https://www.espn.com.br/futebol/time/elenco/_/id/2029",
    "Red Bull Bragantino": "https://www.espn.com.br/futebol/time/elenco/_/id/6079",
    "Remo": "https://www.espn.com.br/futebol/time/elenco/_/id/4936",
    "Santos": "https://www.espn.com.br/futebol/time/elenco/_/id/2674",
    "São Paulo": "https://www.espn.com.br/futebol/time/elenco/_/id/2026",
    "Vasco da Gama": "https://www.espn.com.br/futebol/time/elenco/_/id/3454",
    "Vitória": "https://www.espn.com.br/futebol/time/elenco/_/id/3457",
}


class ElencoGoleirosBronzePipeline(BasePipeline):
    """Pipeline Bronze para dados dos goleiros do Brasileirão."""

    def __init__(self, max_retries: int = 3, retry_delay: int = 3):
        super().__init__("bronze_elenco_goleiros")
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _fetch_with_retry(self, url: str) -> requests.Response:
        """Faz requisição HTTP com retry em caso de falha."""
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                return response
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ) as e:
                wait_time = self.retry_delay * (2**attempt)
                logger.warning(
                    f"Tentativa {attempt + 1}/{self.max_retries} falhou: {e}. Esperando {wait_time}s..."
                )
                time.sleep(wait_time)
        raise requests.RequestException(f"Falha após {self.max_retries} tentativas")

    def _clean_player_name(self, nome_completo: str) -> str:
        """Remove números do nome do jogador."""
        return re.sub(r"\d+", "", nome_completo).strip()

    def _parse_goalkeeper_table(self, table, time: str) -> list:
        """Parse tabela de goleiros."""
        players = []
        rows = table.select("tbody tr")

        for tr in rows:
            tds = tr.select("td")
            if not tds or len(tds) < 2:
                continue

            try:
                nome_completo = tds[0].get_text(strip=True)
                nome = self._clean_player_name(nome_completo)

                if not nome:
                    continue

                player = {
                    "Nome": nome,
                    "Time": time,
                    "POS": tds[1].get_text(strip=True) if len(tds) > 1 else "-",
                    "Idade": tds[2].get_text(strip=True) if len(tds) > 2 else "-",
                    "Alt": tds[3].get_text(strip=True) if len(tds) > 3 else "-",
                    "P": tds[4].get_text(strip=True) if len(tds) > 4 else "-",
                    "NAC": tds[5].get_text(strip=True) if len(tds) > 5 else "-",
                    "J": tds[6].get_text(strip=True) if len(tds) > 6 else "-",
                    "SUB": tds[7].get_text(strip=True) if len(tds) > 7 else "-",
                    "D": tds[8].get_text(strip=True) if len(tds) > 8 else "-",
                    "GS": tds[9].get_text(strip=True) if len(tds) > 9 else "-",
                    "A": tds[10].get_text(strip=True) if len(tds) > 10 else "-",
                    "FC": tds[11].get_text(strip=True) if len(tds) > 11 else "-",
                    "FS": tds[12].get_text(strip=True) if len(tds) > 12 else "-",
                    "CA": tds[13].get_text(strip=True) if len(tds) > 13 else "-",
                    "CV": tds[14].get_text(strip=True) if len(tds) > 14 else "-",
                }

                players.append(player)

            except Exception as e:
                logger.debug(f"Erro ao processar goleiro: {e}")
                continue

        return players

    def _show_team_table(self, console, team_name: str, goleiros: list):
        """Exibe tabela de goleiros de um time específico."""
        # Cores estilo GitHub Dark
        table = Table(
            title=f"[bold cyan]🧤 {team_name}[/bold cyan] - [yellow]Goleiros[/yellow]",
            title_style="bold",
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            border_style="cyan",
            style="on #0d1117",
        )

        # Cores para as colunas
        table.add_column("Nome", style="green bold", width=28)
        table.add_column("POS", justify="center", style="cyan", width=5)
        table.add_column("Idade", justify="center", style="white", width=6)
        table.add_column("Alt", justify="center", style="white", width=6)
        table.add_column("P", justify="center", style="white", width=5)
        table.add_column("NAC", justify="center", style="yellow", width=10)
        table.add_column("J", justify="center", style="green", width=4)
        table.add_column("SUB", justify="center", style="green", width=5)
        table.add_column("D", justify="center", style="red", width=4)
        table.add_column("GS", justify="center", style="red", width=4)
        table.add_column("A", justify="center", style="blue", width=4)
        table.add_column("FC", justify="center", style="white", width=4)
        table.add_column("FS", justify="center", style="white", width=4)
        table.add_column("CA", justify="center", style="yellow", width=4)
        table.add_column("CV", justify="center", style="red", width=4)

        for g in goleiros:
            table.add_row(
                g.get("Nome", "-"),
                g.get("POS", "-"),
                g.get("Idade", "-"),
                g.get("Alt", "-"),
                g.get("P", "-"),
                g.get("NAC", "-"),
                g.get("J", "-"),
                g.get("SUB", "-"),
                g.get("D", "-"),
                g.get("GS", "-"),
                g.get("A", "-"),
                g.get("FC", "-"),
                g.get("FS", "-"),
                g.get("CA", "-"),
                g.get("CV", "-"),
            )

        console.print(table)

    def extract(self, **kwargs) -> pd.DataFrame:
        """Extrai dados dos goleiros da ESPN."""
        console = Console(force_terminal=True, file=sys.stdout)

        console.print("[bold cyan]🧤 GOLEIROS - BRASILEIRÃO 2026[/bold cyan]")

        logger.info("=" * 60)
        logger.info("🏃 INICIANDO: Extração de Goleiros - Bronze")
        logger.info("=" * 60)

        all_goalkeepers = []
        team_data = {}

        for team_name, url in TEAMS_URLS.items():
            try:
                logger.info(f"Extraindo goleiros do {team_name}...")

                response = self._fetch_with_retry(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                tabelas = soup.find_all("table", class_="Table")

                if len(tabelas) < 1:
                    logger.warning(f"Tabelas não encontradas para {team_name}")
                    continue

                # Primeira tabela = goleiros
                goleiros = self._parse_goalkeeper_table(tabelas[0], team_name)
                all_goalkeepers.extend(goleiros)
                team_data[team_name] = goleiros

                logger.info(f"✅ {team_name}: {len(goleiros)} goleiros extraídos")

                time.sleep(2)

            except Exception as e:
                logger.error(f"❌ Erro ao extrair {team_name}: {e}")
                continue

        # Exibir tabelas Rich para todos os 20 times
        console.print("\n")
        for team_name in sorted(team_data.keys()):
            goleiros = team_data[team_name]
            if goleiros:
                self._show_team_table(console, team_name, goleiros)
                console.print("\n")

        df = pd.DataFrame(all_goalkeepers)

        # Resumo final
        console.print(
            f"[bold green]✅ Extração Concluída[/bold green] - Total: {len(df)} goleiros"
        )

        logger.info(f"Total de goleiros extraídos: {len(df)}")
        return df

    def transform(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Transforma os dados (Bronze = dados brutos, sem transformação)."""
        logger.info(f"Transformando {len(df)} registros (Bronze - dados brutos)")
        return df

    def load(self, df: pd.DataFrame, **kwargs) -> Path:
        """Salva os dados em formato Parquet."""
        output_path = settings.bronze_path / "elenco_goleiros.parquet"
        df.to_parquet(output_path, index=False)
        logger.info(f"✅ Dados salvos em: {output_path}")
        return output_path


def run():
    """Executa o pipeline Bronze de goleiros."""
    pipeline = ElencoGoleirosBronzePipeline()
    return pipeline.run()


if __name__ == "__main__":
    run()
