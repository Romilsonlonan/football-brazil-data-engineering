"""Pipeline Bronze - Elenco."""

from pathlib import Path
import time
import re

import pandas as pd
import requests

from src.pipelines.bronze.base import BasePipeline
from src.configs import settings
from src.utils.logger import logger


# URLs dos times do Brasileirão 2026 - IDs obtidos da API ESPN (20 times)
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


class ElencoBronzePipeline(BasePipeline):
    """
    Pipeline Bronze para dados de elenco do Brasileirão.
    """

    def __init__(self, max_retries: int = 5, retry_delay: int = 5):
        super().__init__("bronze_elenco")
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                " AppleWebKit/537.36 (KHTML, like Gecko)"
                " Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logger.info("Pipeline Bronze Elenco inicializado")
        logger.warning(
            " bronze_elenco:bronze - Este pipeline faz apenas extração para visualização"
        )

    def _fetch_with_retry(self, url: str) -> requests.Response:
        """Faz requisição HTTP com retry em caso de falha de rede."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                return response
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError,
            ) as e:
                last_exception = e
                wait_time = self.retry_delay * (2**attempt)
                logger.warning(
                    f"Tentativa {attempt + 1}/{self.max_retries} falhou para {url}: {e}. "
                    f"Esperando {wait_time}s..."
                )
                time.sleep(wait_time)

        raise last_exception or requests.RequestException(
            f"Falha após {self.max_retries} tentativas"
        )

    def _clean_player_name(self, nome_completo: str) -> str:
        """Remove números do nome do jogador mantendo o nome completo."""
        nome_limpo = re.sub(r"\d+", "", nome_completo).strip()
        return nome_limpo

    def extract(self, **kwargs) -> pd.DataFrame:
        """Extrai dados da fonte (scraper ESPN)."""
        from bs4 import BeautifulSoup
        from rich.console import Console
        from rich.panel import Panel

        console = Console(force_terminal=True)

        console.print(
            Panel.fit(
                "[bold cyan]👥 ELENCO BRASILEIRÃO 2026 (20 TIMES)[/bold cyan]\n"
                "[dim]Dados extraídos da ESPN[/dim]",
                border_style="cyan",
                title="🏆 Elenco Times",
            )
        )

        all_players = []
        successful_teams = []
        team_data = {}

        for team_name, url in TEAMS_URLS.items():
            try:
                console.print(f"[cyan]Extraindo elenco do {team_name}...[/cyan]")

                response = self._fetch_with_retry(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                tabelas = soup.find_all("table", class_="Table")

                if len(tabelas) < 2:
                    logger.warning(f"Tabelas não encontradas para {team_name}")
                    console.print(
                        f"[yellow]⚠️ Tabelas não encontradas para {team_name}[/yellow]"
                    )
                    continue

                goleiros = self._parse_goalkeeper_table(tabelas[0], team_name)
                all_players.extend(goleiros)

                jogadores_campo = self._parse_field_player_table(tabelas[1], team_name)
                all_players.extend(jogadores_campo)

                team_data[team_name] = {
                    "goleiros": goleiros,
                    "jogadores": jogadores_campo,
                }

                successful_teams.append(team_name)
                console.print(
                    f"[green]✅ {team_name}: {len(goleiros)} goleiros, {len(jogadores_campo)} jogadores de campo[/green]"
                )

                time.sleep(2)

            except Exception as e:
                logger.error(f"Erro ao extrair {team_name}: {e}")
                console.print(f"[red]❌ Erro ao extrair {team_name}: {e}[/red]")
                continue

        # Salvar dados detalhados em arquivo (sem exibir no terminal para evitar corte)
        self._save_team_tables_to_file(team_data)

        df = pd.DataFrame(all_players)

        self._show_summary(console, df, successful_teams)

        return df

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
                    "Posição": "Goleiro",
                }

                if len(tds) > 1:
                    player["POS"] = tds[1].get_text(strip=True)
                if len(tds) > 2:
                    player["Idade"] = tds[2].get_text(strip=True)
                if len(tds) > 3:
                    player["Alt"] = tds[3].get_text(strip=True)
                if len(tds) > 4:
                    player["P"] = tds[4].get_text(strip=True)
                if len(tds) > 5:
                    player["NAC"] = tds[5].get_text(strip=True)
                if len(tds) > 6:
                    player["J"] = tds[6].get_text(strip=True)
                if len(tds) > 7:
                    player["SUB"] = tds[7].get_text(strip=True)
                if len(tds) > 8:
                    player["D"] = tds[8].get_text(strip=True)
                if len(tds) > 9:
                    player["GS"] = tds[9].get_text(strip=True)
                if len(tds) > 10:
                    player["A"] = tds[10].get_text(strip=True)
                if len(tds) > 11:
                    player["FC"] = tds[11].get_text(strip=True)
                if len(tds) > 12:
                    player["FS"] = tds[12].get_text(strip=True)
                if len(tds) > 13:
                    player["CA"] = tds[13].get_text(strip=True)
                if len(tds) > 14:
                    player["CV"] = tds[14].get_text(strip=True)

                players.append(player)

            except Exception as e:
                logger.debug(f"Erro ao processar goleiro: {e}")
                continue

        return players

    def _parse_field_player_table(self, table, time: str) -> list:
        """Parse tabela de jogadores de campo."""

        players = []
        rows = table.select("tbody tr")

        posicoes = {"G": "Goleiro", "D": "Defensor", "M": "Meia", "A": "Atacante"}

        for tr in rows:
            tds = tr.select("td")
            if not tds or len(tds) < 2:
                continue

            try:
                nome_completo = tds[0].get_text(strip=True)
                nome = self._clean_player_name(nome_completo)

                if not nome:
                    continue

                pos_abbr = tds[1].get_text(strip=True) if len(tds) > 1 else "D"
                posicao_completa = posicoes.get(pos_abbr, "Jogador de Campo")

                player = {
                    "Nome": nome,
                    "Time": time,
                    "Posição": posicao_completa,
                }

                if len(tds) > 1:
                    player["POS"] = tds[1].get_text(strip=True)
                if len(tds) > 2:
                    player["Idade"] = tds[2].get_text(strip=True)
                if len(tds) > 3:
                    player["Alt"] = tds[3].get_text(strip=True)
                if len(tds) > 4:
                    player["P"] = tds[4].get_text(strip=True)
                if len(tds) > 5:
                    player["NAC"] = tds[5].get_text(strip=True)
                if len(tds) > 6:
                    player["J"] = tds[6].get_text(strip=True)
                if len(tds) > 7:
                    player["SUB"] = tds[7].get_text(strip=True)
                if len(tds) > 8:
                    player["G"] = tds[8].get_text(strip=True)
                if len(tds) > 9:
                    player["A"] = tds[9].get_text(strip=True)
                if len(tds) > 10:
                    player["TC"] = tds[10].get_text(strip=True)
                if len(tds) > 11:
                    player["CG"] = tds[11].get_text(strip=True)
                if len(tds) > 12:
                    player["FC"] = tds[12].get_text(strip=True)
                if len(tds) > 13:
                    player["FS"] = tds[13].get_text(strip=True)
                if len(tds) > 14:
                    player["CA"] = tds[14].get_text(strip=True)
                if len(tds) > 15:
                    player["CV"] = tds[15].get_text(strip=True)

                players.append(player)

            except Exception as e:
                logger.debug(f"Erro ao processar jogador: {e}")
                continue

        return players

    def _save_team_tables_to_file(self, team_data: dict):
        """Salva as tabelas detalhadas em arquivo de texto."""
        output_file = settings.bronze_path / "elenco_detalhado.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 100 + "\n")
            f.write("ELENCO BRASILEIRÃO 2026 - DETALHAMENTO DOS 20 TIMES\n")
            f.write("=" * 100 + "\n\n")

        for team_name, data in team_data.items():
            goleiros = data["goleiros"]
            jogadores = data["jogadores"]

            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"TIME: {team_name}\n")
                f.write(f"{'='*80}\n")

            if goleiros:
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write("\nGOLEIROS:\n")
                    f.write(
                        f"{'Nome':<30} {'POS':<5} {'Idade':<6} {'Alt':<7} {'P':<7} {'NAC':<10} {'J':<5} {'SUB':<5} {'D':<5} {'GS':<5} {'A':<5} {'FC':<5} {'FS':<5} {'CA':<5} {'CV':<5}\n"
                    )
                    for g in goleiros:
                        f.write(
                            f"{g.get('Nome', ''):<30} {g.get('POS', '-'):<5} {g.get('Idade', '-'):<6} {g.get('Alt', '-'):<7} {g.get('P', '-'):<7} {g.get('NAC', '-')[:10]:<10} {g.get('J', '-'):<5} {g.get('SUB', '-'):<5} {g.get('D', '-'):<5} {g.get('GS', '-'):<5} {g.get('A', '-'):<5} {g.get('FC', '-'):<5} {g.get('FS', '-'):<5} {g.get('CA', '-'):<5} {g.get('CV', '-'):<5}\n"
                        )

            if jogadores:
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write("\nJOGADORES DE CAMPO:\n")
                    f.write(
                        f"{'Nome':<30} {'POS':<5} {'Idade':<6} {'Alt':<7} {'P':<7} {'NAC':<10} {'J':<5} {'SUB':<5} {'G':<5} {'A':<5} {'TC':<5} {'CG':<5} {'FC':<5} {'FS':<5} {'CA':<5} {'CV':<5}\n"
                    )
                    for j in jogadores:
                        f.write(
                            f"{j.get('Nome', ''):<30} {j.get('POS', '-'):<5} {j.get('Idade', '-'):<6} {j.get('Alt', '-'):<7} {j.get('P', '-'):<7} {j.get('NAC', '-')[:10]:<10} {j.get('J', '-'):<5} {j.get('SUB', '-'):<5} {j.get('G', '-'):<5} {j.get('A', '-'):<5} {j.get('TC', '-'):<5} {j.get('CG', '-'):<5} {j.get('FC', '-'):<5} {j.get('FS', '-'):<5} {j.get('CA', '-'):<5} {j.get('CV', '-'):<5}\n"
                        )

        print(f"\n📄 Arquivo detalhado salvo em: {output_file}\n")

    def _show_summary(self, console, df: pd.DataFrame, successful_teams: list):
        """Exibe o resumo geral dos elencos."""
        from rich.table import Table
        from rich.panel import Panel
        from rich import box

        console.print("\n")
        console.print(
            Panel.fit(
                "[bold cyan]📊 RESUMO DOS ELENCOS (20 TIMES)[/bold cyan]",
                border_style="cyan",
            )
        )

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Time", style="yellow", width=22)
        table.add_column("Goleiros", style="cyan", justify="center", width=10)
        table.add_column("Jogadores", style="cyan", justify="center", width=10)
        table.add_column("Total", style="bold green", justify="center", width=10)

        for time_nome in sorted(df["Time"].unique()):
            time_df = df[df["Time"] == time_nome]
            goleiros = len(time_df[time_df["Posição"] == "Goleiro"])
            jogadores = len(time_df[time_df["Posição"] != "Goleiro"])
            table.add_row(
                time_nome, str(goleiros), str(jogadores), str(goleiros + jogadores)
            )

        console.print(table)
        console.print(f"\n[dim]Total de jogadores extraídos: {len(df)}[/dim]")
        console.print(
            f"[dim]Times extraídos com sucesso: {len(successful_teams)}/{len(TEAMS_URLS)}[/dim]"
        )

    def transform(self, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        logger.info("Transformando dados de elenco...")
        logger.warning(
            "Transformação não implementada - passando dados direto para load"
        )
        return df

    def load(self, df: pd.DataFrame, table_name: str = "elenco", **kwargs) -> Path:
        output_path = settings.bronze_path / f"{table_name}.parquet"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        logger.info(f"Dados salvos em: {output_path}")
        return output_path

    def run(self, **kwargs) -> Path:
        logger.info("=" * 60)
        logger.info("INICIANDO PIPELINE BRONZE - ELENCO (20 TIMES)")
        logger.info("=" * 60)

        try:
            df = self.extract(**kwargs)
            df = self.transform(df, **kwargs)
            output_path = self.load(df, **kwargs)

            logger.info("=" * 60)
            logger.info("PIPELINE BRONZE - ELENCO CONCLUIDO")
            logger.info("=" * 60)

            return output_path

        except Exception as e:
            logger.error(f"Pipeline falhou: {e}")
            raise


def run():
    pipeline = ElencoBronzePipeline()
    pipeline.run()


if __name__ == "__main__":
    run()
