"""
Análise Exploratória — Óbitos Santa Cruz/RJ 2026
Leitura e diagnóstico dos 3 arquivos CSV (SIM)
"""

import pandas as pd
from pathlib import Path

# ─── Configuração ───────────────────────────────────────────────
ARQUIVOS = {
    "MATERNO":  Path("MATERNO RESIDÊNCIA 2026.csv"),
    "FETAL":    Path("FETAL RESIDÊNCIA 2026.csv"),
    "INFANTIL": Path("INFANTIL RESIDÊNCIA 2026.csv"),
}

SEPARADOR = ";"
ENCODING = "utf-8-sig"  # remove BOM automaticamente


def carregar(nome: str, caminho: Path) -> pd.DataFrame:
    """Lê CSV com configuração correta para dados SIM/SVS."""
    df = pd.read_csv(caminho, sep=SEPARADOR, encoding=ENCODING, low_memory=False)
    print(f"\n{'='*70}")
    print(f"  {nome}")
    print(f"  Arquivo: {caminho.name}")
    print(f"{'='*70}")

    # Shape
    linhas, colunas = df.shape
    print(f"\n  Linhas: {linhas}  |  Colunas: {colunas}")

    # Primeiras linhas
    print(f"\n  ── Primeiras 5 linhas ──")
    print(df.head().to_string())

    # Nomes das colunas
    print(f"\n  ── Colunas ({len(df.columns)}) ──")
    for i, col in enumerate(df.columns, 1):
        print(f"    {i:>3}. {col}")

    # Tipos de dados
    print(f"\n  ── Tipos de dados ──")
    tipos = df.dtypes.value_counts()
    for tipo, qtd in tipos.items():
        print(f"    {tipo}: {qtd} colunas")

    print(f"\n  ── Detalhe por coluna ──")
    for col in df.columns:
        nulos = df[col].isnull().sum()
        nulos_pct = (nulos / linhas) * 100
        n_unique = df[col].nunique()
        print(f"    {col:<45} | tipo: {str(df[col].dtype):<10} | únicos: {n_unique:>5} | nulos: {nulos:>5} ({nulos_pct:5.1f}%)")

    # Missing values resumo
    cols_com_nulos = df.columns[df.isnull().any()]
    print(f"\n  ── Colunas com valores nulos: {len(cols_com_nulos)} ──")
    if len(cols_com_nulos) > 0:
        nulos_df = df[cols_com_nulos].isnull().sum().sort_values(ascending=False)
        for col, qtd in nulos_df.items():
            pct = (qtd / linhas) * 100
            flag = " ***" if pct > 50 else ""
            print(f"    {col:<45} | nulos: {qtd:>5} ({pct:5.1f}%){flag}")
    else:
        print("    Nenhum valor nulo encontrado.")

    print()
    return df


# ─── Execução ───────────────────────────────────────────────────
def main():
    print("\n" + "█"*70)
    print("  EXPLORAÇÃO DE DADOS — ÓBITOS SANTA CRUZ/RJ 2026")
    print("█"*70)

    dataframes = {}
    for nome, caminho in ARQUIVOS.items():
        if not caminho.exists():
            print(f"\n  [ERRO] Arquivo não encontrado: {caminho}")
            continue
        dataframes[nome] = carregar(nome, caminho)

    # Resumo geral
    if dataframes:
        print("\n" + "="*70)
        print("  RESUMO GERAL")
        print("="*70)
        total = sum(df.shape[0] for df in dataframes.values())
        print(f"\n  Total de registros: {total}")
        for nome, df in dataframes.items():
            print(f"    {nome:<12} → {df.shape[0]:>3} registros, {df.shape[1]} colunas")

    print("\n  Concluído.\n")


if __name__ == "__main__":
    main()
