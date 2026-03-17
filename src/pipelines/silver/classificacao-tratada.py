"""Pipeline Silver - Classificação."""

import pandas as pd
from pathlib import Path
import re

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from src.configs import settings
from src.utils.logger import logger
from src.security.data_scanner import DataSecurityScanner


def run():
    """Executa o pipeline de limpeza dos dados de classificação."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🧹 PIPELINE SILVER - CLASSIFICAÇÃO TRATADA[/bold cyan]\n"
        "[dim]Limpeza e tratamento de dados[/dim]",
        border_style="cyan",
        title="⚙️ ETL Silver"
    ))
    
    logger.info("=" * 60)
    logger.info("INICIANDO PIPELINE SILVER - CLASSIFICACAO")
    logger.info("=" * 60)
    
    # Ler dados do bronze
    bronze_path = settings.bronze_path / "classificacao.parquet"
    logger.info(f"Lendo dados de: {bronze_path}")
    
    if not bronze_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {bronze_path}")
    
    df = pd.read_parquet(bronze_path)
    
    logger.info(f"Dados originais: {len(df)} linhas")
    logger.info(f"Colunas: {df.columns.tolist()}")
    
    # ============================================
    # RELATÓRIO DE DIAGNÓSTICO ANTES DA LIMPEZA
    # ============================================
    logger.info("")
    logger.info("=" * 60)
    logger.info("🔍 RELATÓRIO DE DIAGNÓSTICO - ANTES DA LIMPEZA")
    logger.info("=" * 60)
    
    # Verificar valores nulos
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    
    # Validar colunas obrigatórias
    required_cols = ['Posição', 'Time']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias ausentes no DataFrame: {missing_cols}")
    
    logger.info(f"📊 Total de valores NULOS: {total_nulls}")
    if total_nulls > 0:
        for col, count in null_counts[null_counts > 0].items():
            logger.warning(f"   Coluna '{col}': {count} valores nulos")
    else:
        logger.info("   ✅ Nenhum valor nulo encontrado")
    
    # Verificar strings vazias em colunas numéricas
    numeric_cols = [col for col in df.columns if col not in ['Posição', 'Time']]
    for col in numeric_cols:
        # Converter para string e verificar vazias
        str_col = df[col].astype(str)
        empty_count = (str_col == '').sum()
        nan_count = str_col.str.lower().eq('nan').sum()
        none_count = str_col.str.lower().eq('none').sum()
        
        total_issues = empty_count + nan_count + none_count
        if total_issues > 0:
            logger.warning(f"   Coluna '{col}': {total_issues} valores problemáticos (vazios={empty_count}, nan={nan_count}, none={none_count})")
    
    # Verificar caracteres especiais em nomes de times
    if 'Time' in df.columns:
        #Regex alinhada com clean_team_name: remove todos os caracteres especiais
        special_char_pattern = re.compile(r'[^\w\sáéíóúàèìòùãẽĩõũâêîôûç-]')
        teams_with_special = []
        for idx, time in df['Time'].items():
            if special_char_pattern.search(str(time)):
                teams_with_special.append((idx, time))
        
        if teams_with_special:
            logger.warning(f"   {len(teams_with_special)} times com caracteres especiais:")
            for idx, time in teams_with_special:
                logger.warning(f"      Linha {idx}: '{time}'")
        else:
            logger.info("   ✅ Nenhum nome de time com caracteres especiais")
    
    logger.info("")
    logger.info("📋 Dados originais (antes da limpeza):")
    console.print("\n[bold]Dados Originais:[/bold]")
    console.print(df.to_string())
    
    # Transformação: Limpeza e higienização
    df_clean = clean_classificacao(df)
    
    # ============================================
    # VERIFICAÇÃO DE SEGURANÇA (PII Detection)
    # ============================================
    logger.info("")
    try:
        logger.info("🔒 Executando verificação de segurança...")
        scanner = DataSecurityScanner()
        security_result = scanner.scan_dataframe(df_clean, "classificacao_silver")
        
        if security_result.has_risks:
            logger.critical("⚠️ Dados sensíveis detectados! Pipeline continuará mas requer revisão.")
            # Não bloqueia o pipeline, apenas alerta
        else:
            logger.info("✅ Verificação de segurança passed")
            
    except Exception as e:
        logger.warning(f"⚠️ Scanner de segurança indisponível: {e}")
        logger.info("   Continuando pipeline normalmente...")
    
    # ============================================
    # RELATÓRIO DE DIAGNÓSTICO DEPOIS DA LIMPEZA
    # ============================================
    logger.info("")
    logger.info("=" * 60)
    console.print(Panel.fit(
        "[bold green]✅ RELATÓRIO DE DIAGNÓSTICO - DEPOIS DA LIMPEZA[/bold green]",
        border_style="green",
        title="🔍 Diagnóstico"
    ))
    logger.info("=" * 60)
    logger.info(f"Total de linhas processadas: {len(df_clean)}")
    logger.info(f"Linhas removidas (duplicatas): {len(df) - len(df_clean)}")
    
    # Verificar valores nulos
    null_counts_after = df_clean.isnull().sum()
    total_nulls_after = null_counts_after.sum()
    logger.info(f"📊 Total de valores NULOS: {total_nulls_after}")
    if total_nulls_after > 0:
        for col, count in null_counts_after[null_counts_after > 0].items():
            logger.warning(f"   Coluna '{col}': {count} valores nulos")
    else:
        logger.info("   ✅ Nenhum valor nulo encontrado")
    
    # Verificar strings vazias (usar colunas após renomeação)
    numeric_cols_after = [col for col in df_clean.columns if col not in ['Posição', 'Time']]
    for col in numeric_cols_after:
        str_col = df_clean[col].astype(str)
        empty_count = (str_col == '').sum()
        if empty_count > 0:
            logger.warning(f"   Coluna '{col}': {empty_count} strings vazias")
    
    # Mostrar dados limpos
    logger.info("")
    logger.info("📋 Dados limpos (após limpeza):")
    
    # Criar tabela de resultados
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Pos", style="cyan", justify="center", width=4)
    table.add_column("Time", style="yellow", width=20)
    table.add_column("Jogos", style="white", justify="center", width=5)
    table.add_column("Vitórias", style="green", justify="center", width=7)
    table.add_column("Empates", style="yellow", justify="center", width=7)
    table.add_column("Derrotas", style="red", justify="center", width=8)
    table.add_column("GolsPro", style="white", justify="center", width=7)
    table.add_column("GolsCon", style="white", justify="center", width=8)
    table.add_column("Saldo", style="white", justify="center", width=6)
    table.add_column("Pontos", style="bold cyan", justify="center", width=7)
    
    for _, row in df_clean.head(20).iterrows():
        pos_style = "bold green" if row["Posição"] <= 4 else \
                   "bold yellow" if row["Posição"] <= 6 else \
                   "bold red" if row["Posição"] >= 17 else ""
        
        table.add_row(
            str(row["Posição"]),
            row["Time"][:18],
            str(row["Jogos"]),
            str(row["Vitorias"]),
            str(row["Empates"]),
            str(row["Derrotas"]),
            str(row["GolsPro"]),
            str(row["GolsContra"]),
            str(row["SaldoGols"]),
            str(row["Pontos"]),
        )
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]📊 TABELA CLASSIFICAÇÃO TRATADA[/bold cyan]",
        border_style="cyan",
        title="🏆 Resultado"
    ))
    console.print(table)
    console.print(f"\n[dim]Mostrando {len(df_clean)} times[/dim]")
    
    # Salvar no diretório silver
    output_path = settings.silver_path / "classificacao-limpa.parquet"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_parquet(output_path, index=False)
    logger.info(f"Dados limpos salvos em: {output_path}")
    
    logger.info("=" * 60)
    console.print(Panel.fit(
        "[bold green]🎉 PIPELINE SILVER - CLASSIFICAÇÃO CONCLUÍDO[/bold green]\n"
        f"[dim]Arquivo salvo em: {output_path}[/dim]",
        border_style="green",
        title="✅ Sucesso"
    ))
    logger.info("=" * 60)
    logger.info("PIPELINE SILVER - CLASSIFICACAO CONCLUIDO")
    logger.info("=" * 60)
    
    return output_path


def clean_classificacao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e higieniza os dados de classificação.
    
    - Remove caracteres especiais dos nomes de times
    - Substitui valores vazios/nulos por 0 em colunas numéricas
    - Garante que colunas numéricas sejam do tipo correto
    """
    df_clean = df.copy()
    
    # 1. Limpar nomes de times (remover caracteres especiais)
    if 'Time' in df_clean.columns:
        logger.info("")
        logger.info("🧹 ETAPA 1: Limpando nomes de times...")
        original_times = df_clean['Time'].tolist()
        df_clean['Time'] = df_clean['Time'].apply(clean_team_name)
        
        # Mostrar mudanças
        changes = []
        for i, (orig, clean) in enumerate(zip(original_times, df_clean['Time'])):
            if orig != clean:
                changes.append(f"'{orig}' → '{clean}'")
        
        if changes:
            for change in changes:
                logger.info(f"   {change}")
            logger.info(f"   Total: {len(changes)} time(s) modificado(s)")
        else:
            logger.info("   Nenhuma modificação necessária")
        logger.info("✅ Nomes de times limpos")
    
    # 2. Identificar colunas numéricas (excluindo Posição e Time)
    numeric_columns = [col for col in df_clean.columns if col not in ['Posição', 'Time']]
    
    # 3. Substituir valores vazios, nulos ou com caracteres especiais por 0
    logger.info("")
    logger.info("🧹 ETAPA 2: Limpando colunas numéricas...")
    for col in numeric_columns:
        # Contar valores antes (como string para capturar todos os casos)
        str_col_original = df_clean[col].astype(str)
        null_before = str_col_original.isnull().sum()
        empty_before = (str_col_original == '').sum()
        nan_before = str_col_original.str.lower().eq('nan').sum()
        none_before = str_col_original.str.lower().eq('none').sum()
        dash_before = (str_col_original == '-').sum()
        
        total_issues_before = empty_before + nan_before + none_before + dash_before
        
        # Converter para string primeiro para poder fazer a limpeza
        df_clean[col] = df_clean[col].astype(str)
        
        # Substituir valores vazios, 'nan', 'None', strings vazias por '0'
        df_clean[col] = df_clean[col].replace(['', 'nan', 'None', 'NaN', 'null', '-'], '0')
        
        # Remover caracteres não numéricos (exceto dígitos e ponto decimal)
        df_clean[col] = df_clean[col].apply(lambda x: re.sub(r'[^\d.-]', '', str(x)) if pd.notna(x) else '0')
        
        # Substituir strings vazias após limpeza por '0'
        df_clean[col] = df_clean[col].replace('', '0')
        
        # Converter para numérico (int64 para evitar overflow)
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0).astype('int64')
        
        # Contar valores depois
        null_after = df_clean[col].isnull().sum()
        
        if total_issues_before > 0:
            logger.info(f"   Coluna '{col}': {total_issues_before} valores substituídos por 0")
        else:
            logger.info(f"   Coluna '{col}': Sem problemas encontrados")
    
    logger.info(f"✅ Colunas numéricas limpas: {numeric_columns}")
    
    # 4. Remover linhas duplicadas
    logger.info("")
    logger.info("🧹 ETAPA 3: Removendo duplicatas...")
    original_len = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    if len(df_clean) < original_len:
        logger.info(f"   Removidas {original_len - len(df_clean)} linhas duplicadas")
    else:
        logger.info("   Nenhuma duplicata encontrada")
    
    # 5. Ordenar por Pontos (PTS) decrescente
    logger.info("")
    logger.info("🧹 ETAPA 4: Ordenando por pontos...")
    if 'PTS' in df_clean.columns:
        df_clean = df_clean.sort_values('PTS', ascending=False).reset_index(drop=True)
        logger.info("   Times ordenados por PTS (maior para menor)")
    
    # 6. Recalcular a Posição baseada na ordem
    df_clean['Posição'] = range(1, len(df_clean) + 1)
    logger.info("   Posições recalculadas")
    
    # 7. Renomear colunas conforme glossário
    logger.info("")
    logger.info("🧹 ETAPA 5: Renomeando colunas...")
    column_rename = {
        'J': 'Jogos',
        'V': 'Vitorias',
        'E': 'Empates',
        'D': 'Derrotas',
        'GP': 'GolsPro',
        'GC': 'GolsContra',
        'SG': 'SaldoGols',
        'PTS': 'Pontos'
    }
    df_clean = df_clean.rename(columns=column_rename)
    logger.info(f"   Colunas renomeadas: {list(column_rename.values())}")
    
    logger.info("")
    logger.info(f"✅ Dados limpos: {len(df_clean)} linhas")
    
    return df_clean


def clean_team_name(name: str) -> str:
    """Remove caracteres especiais do nome do time."""
    if pd.isna(name):
        return "Desconhecido"
    
    # Converter para string
    name = str(name)
    
    # Remover caracteres especiais, mantendo apenas letras, números e espaços
    name = re.sub(r'[^\w\s]', '', name)
    
    # Remover espaços extras
    name = ' '.join(name.split())
    
    return name.strip() if name.strip() else "Desconhecido"


if __name__ == "__main__":
    run()
