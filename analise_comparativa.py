"""Análise comparativa para presentation update"""
import pandas as pd
PASTA = "dados_limpos"

for base in ['materno','fetal','infantil']:
    df = pd.read_csv(f'{PASTA}/{base}_limpo.csv', sep=';', encoding='utf-8-sig', low_memory=False)
    print(f"\n{'='*60}")
    print(f"  {base.upper()} ({len(df)} registros)")
    print(f"{'='*60}")

    # Bairro residência
    if 'BAIRES' in df.columns:
        bairros = df['BAIRES'].value_counts()
        print(f"\n  Bairros residência:")
        for b, q in bairros.head(8).items():
            print(f"    {b}: {q}")

    # Local ocorrência
    if 'LOCAL DE OCORRENCIA' in df.columns:
        print(f"\n  Local ocorrência:")
        for l, q in df['LOCAL DE OCORRENCIA'].value_counts().head(8).items():
            print(f"    {l}: {q}")

    # Sexo (só infantil tem)
    if 'SEXO' in df.columns:
        sexo = df['SEXO'].value_counts()
        print(f"\n  Sexo:")
        for s, q in sexo.items():
            label = {'M':'Masculino','F':'Feminino'}.get(s, s)
            print(f"    {label}: {q} ({q/len(df)*100:.0f}%)")

    # Idade mãe
    if 'IDADEMAE' in df.columns:
        idades = pd.to_numeric(df['IDADEMAE'], errors='coerce').dropna()
        if len(idades) > 0:
            print(f"\n  Idade mãe: média={idades.mean():.1f} | min={idades.min()} | max={idades.max()}")

    # Unidade referência
    for col in ['UNIDADE REFERENCIA','UNIDADE DE REFERENCIA']:
        if col in df.columns:
            print(f"\n  {col}:")
            vals = df[col].dropna()
            vals = vals[vals != 'Não informado']
            for v, q in vals.value_counts().head(5).items():
                print(f"    {v}: {q}")
            break

    # CID principal
    for col in ['CAUSABAS','CB PÓS INVEST','CB- PÓS INVESTIGAÇÃO']:
        if col in df.columns:
            vals = df[col].dropna()
            vals = vals[vals != 'Não informado']
            if len(vals) > 0:
                print(f"\n  {col}:")
                for c, q in vals.value_counts().head(5).items():
                    print(f"    {c}: {q}")
            break
