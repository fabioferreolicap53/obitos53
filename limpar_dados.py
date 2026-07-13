"""
Limpeza e Preparação — Óbitos Santa Cruz/RJ 2026
Conversão de datas, tratamento de nulos, colunas derivadas
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ─── Configuração ───────────────────────────────────────────────
SEPARADOR = ";"
ENCODING = "utf-8-sig"
PASTA_SAIDA = Path("dados_limpos")
PASTA_SAIDA.mkdir(exist_ok=True)

ARQUIVOS = {
    "MATERNO":  Path("MATERNO RESIDÊNCIA 2026.csv"),
    "FETAL":    Path("FETAL RESIDÊNCIA 2026.csv"),
    "INFANTIL": Path("INFANTIL RESIDÊNCIA 2026.csv"),
}

# Colunas de data conhecidas no SIM (podem variar entre bases)
COLS_DATA = [
    "DTOBITO", "DTNASC", "DTREGCART", "DTATESTADO",
    "DTINVESTIG", "DTCADASTRO", "DTRECEBIM", "DTRESSELE", "DTRECORIG",
    "DTINVESTIG.1",  # duplicata no INFANTIL
]


# ─── Conversão de Datas ────────────────────────────────────────
def serial_excel_para_data(valor):
    """
    Converte serial Excel (número float/int) para datetime.
    Excel epoch: 1899-12-30 (base 0).
    Valores < 1900 ou > 2100 são rejeitados (não são datas válidas).
    """
    if pd.isna(valor):
        return pd.NaT
    try:
        num = float(valor)
    except (ValueError, TypeError):
        return pd.NaT
    if num < 1 or num > 80000:  # ~2119
        return pd.NaT
    try:
        return pd.Timestamp("1899-12-30") + pd.Timedelta(days=num)
    except Exception:
        return pd.NaT


def limpar_e_converter_data(serie: pd.Series) -> pd.Series:
    """
    Converte coluna de data do SIM:
    1. Remove strings-vazia tipo '/ / / / /'
    2. Tenta parse DD/MM/YYYY
    3. Fallback: trata como serial Excel
    """
    # Mascarar valores-vazia do SIM
    padroes_vazio = {"/ / / / /", "/", "", "NA", "NaN"}
    serie = serie.astype(str).str.strip()
    serie = serie.replace(list(padroes_vazio) + ["nan", "None"], np.nan)

    # Tentar parse direto DD/MM/YYYY
    convertido = pd.to_datetime(serie, format="%d/%m/%Y", errors="coerce")

    # Onde falhou e o valor não é nulo → tratar como serial Excel
    mascara_serial = convertido.isna() & serie.notna()
    if mascara_serial.any():
        convertido.loc[mascara_serial] = serie.loc[mascara_serial].apply(
            serial_excel_para_data
        )

    return convertido


# ─── Tratamento de Nulos ────────────────────────────────────────
def tratar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estratégia de nulos:
    - Linhas 100% vazias (todos NaN) → removidas
    - Colunas de texto → 'Não informado'
    - Colunas numéricas → mantém NaN (para análise estatística)
    - Colunas de data → mantém NaT
    """
    # 1. Remover linhas totalmente vazias
    antes = len(df)
    df = df.dropna(how="all")
    removidas = antes - len(df)
    if removidas > 0:
        print(f"    Linhas 100% vazias removidas: {removidas}")

    # 2. Colunas de texto → 'Não informado'
    cols_texto = df.select_dtypes(include=["object", "string"]).columns
    for col in cols_texto:
        df[col] = df[col].fillna("Não informado")

    # 3. Numéricas e datas: mantém NaN/NaT
    return df


# ─── Colunas Derivadas ──────────────────────────────────────────
def criar_colunas_temporais(df: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas 'Ano' e 'Mês' a partir de DTOBITO."""
    if "DTOBITO" in df.columns:
        novas = pd.DataFrame({
            "Ano": df["DTOBITO"].dt.year,
            "Mês": df["DTOBITO"].dt.month,
            "Mês Nome": df["DTOBITO"].dt.month_name(locale="pt_BR"),
            "Dia da Semana": df["DTOBITO"].dt.day_name(locale="pt_BR"),
        }, index=df.index)
        df = pd.concat([df, novas], axis=1)
    return df


# ─── Pipeline Principal ─────────────────────────────────────────
def limpar_base(nome: str, caminho: Path) -> pd.DataFrame | None:
    """Pipeline completo de limpeza para uma base."""
    print(f"\n{'='*60}")
    print(f"  LIMPANDO: {nome}")
    print(f"{'='*60}")

    if not caminho.exists():
        print(f"  [ERRO] Arquivo não encontrado: {caminho}")
        return None

    # Leitura
    df = pd.read_csv(caminho, sep=SEPARADOR, encoding=ENCODING, low_memory=False)
    print(f"  Linhas originais: {len(df)}")
    print(f"  Colunas originais: {len(df.columns)}")

    # Remover coluna-lixo 'Unnamed: 146/147' se existir
    cols_unnamed = [c for c in df.columns if c.startswith("Unnamed")]
    if cols_unnamed:
        df = df.drop(columns=cols_unnamed)
        print(f"  Colunas 'Unnamed' removidas: {len(cols_unnamed)}")

    # Converter datas
    cols_data_existentes = [c for c in COLS_DATA if c in df.columns]
    print(f"\n  Convertendo {len(cols_data_existentes)} colunas de data...")
    for col in cols_data_existentes:
        antes_nulos = df[col].isna().sum()
        df[col] = limpar_e_converter_data(df[col])
        depois_nulos = df[col].isna().sum()
        convertidas = len(df) - depois_nulos
        print(f"    {col:<25} → {convertidas}/{len(df)} convertidas")

    # Tratar nulos
    print(f"\n  Tratando valores nulos...")
    df = tratar_nulos(df)
    print(f"  Linhas finais: {len(df)}")

    # Colunas temporais
    df = criar_colunas_temporais(df)
    if "Ano" in df.columns:
        print(f"\n  Colunas derivadas criadas: Ano, Mês, Mês Nome, Dia da Semana")
        print(f"  Anos: {sorted(df['Ano'].dropna().unique())}")
        print(f"  Meses: {sorted(df['Mês'].dropna().unique())}")

    # Salvar
    saida = PASTA_SAIDA / f"{nome.lower()}_limpo.csv"
    df.to_csv(saida, sep=SEPARADOR, encoding="utf-8-sig", index=False)
    print(f"\n  Salvo: {saida}")

    return df


# ─── Execução ───────────────────────────────────────────────────
def main():
    print("\n" + "█"*60)
    print("  LIMPEZA DE DADOS — ÓBITOS SANTA CRUZ/RJ 2026")
    print("█"*60)

    dataframes = {}
    for nome, caminho in ARQUIVOS.items():
        df = limpar_base(nome, caminho)
        if df is not None:
            dataframes[nome] = df

    # Resumo final
    print("\n" + "="*60)
    print("  RESUMO PÓS-LIMPEZA")
    print("="*60)
    for nome, df in dataframes.items():
        nulos_totais = df.isna().sum().sum()
        print(f"\n  {nome}:")
        print(f"    Shape: {df.shape[0]} linhas × {df.shape[1]} colunas")
        print(f"    Nulos restantes: {nulos_totais}")
        if "DTOBITO" in df.columns:
            datas_validas = df["DTOBITO"].notna().sum()
            print(f"    Datas óbito válidas: {datas_validas}/{len(df)}")
        if "Ano" in df.columns:
            print(f"    Distribuição por mês:")
            for mes, qtd in df["Mês Nome"].value_counts().sort_index().items():
                print(f"      {mes}: {qtd}")

    print("\n  Concluído.\n")
    return dataframes


if __name__ == "__main__":
    main()
