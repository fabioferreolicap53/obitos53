"""
Métricas para Apresentação — Óbitos Santa Cruz/RJ 2026
Cálculos comentados a partir dos DataFrames limpos
"""

import pandas as pd
import numpy as np
from pathlib import Path

SEPARADOR = ";"
ENCODING = "utf-8-sig"
PASTA = Path("dados_limpos")


def carregar(nome: str) -> pd.DataFrame:
    caminho = PASTA / f"{nome}_limpo.csv"
    return pd.read_csv(caminho, sep=SEPARADOR, encoding=ENCODING, low_memory=False)


def sep(titulo: str):
    print(f"\n{'━'*60}")
    print(f"  {titulo}")
    print(f"{'━'*60}")


# ═══════════════════════════════════════════════════════════════
#  1. ÓBITOS MATERNO
# ═══════════════════════════════════════════════════════════════
def metricas_materno():
    sep("1. ÓBITOS MATERNO")
    df = carregar("materno")

    # ── Total e distribuição mensal ──
    print(f"\n  Total de óbitos maternos: {len(df)}")
    print(f"  Período: {df['Ano'].min()}-{df['Ano'].max()}")
    print(f"\n  Distribuição por mês:")
    for mes, qtd in df["Mês Nome"].value_counts().sort_index().items():
        print(f"    {mes}: {qtd}")
    # INTERPRETAÇÃO: Óbitos maternos em Santa Cruz são baixos em volume
    # (n=3), mas cada caso representa falha sistêmica no cuidado perinatal.
    # Janeiro concentra 2/3 dos casos — possível efeito sazonal ou atraso
    # no atendimento pré-natal no período festivo.

    # ── Causas (CID pós-investigação) ──
    print(f"\n  Causas básicas (pós investigação):")
    causa_col = "CAUSABAS" if "CAUSABAS" in df.columns else None
    if causa_col:
        for cid, qtd in df[causa_col].value_counts().head(5).items():
            print(f"    {cid}: {qtd} caso(s)")
    # INTERPRETAÇÃO: CAUSABAS é o CID final definido pelo GT-Comissão.
    # Diferente da causa original (CAUSABAS_O), reflete revisão após
    # investigação epidemiológica — indicador de qualidade do sistema.

    # ── Linha A (causa imediata) ──
    if "LINHAA" in df.columns:
        linhas_a = df["LINHAA"].dropna()
        linhas_a = linhas_a[linhas_a != "Não informado"]
        if len(linhas_a) > 0:
            print(f"\n  Linha A (causa imediata):")
            for la, qtd in linhas_a.value_counts().head(5).items():
                print(f"    {la}: {qtd}")

    # ── Faixa etária da mãe ──
    print(f"\n  Faixa etária da mãe:")
    for _, row in df.iterrows():
        nome = row.get("NOME", "?")
        idade = row.get("IDADEMAE", None)
        if pd.notna(idade) and idade != "Não informado":
            print(f"    {nome}: {int(idade)} anos")
    # INTERPRETAÇÃO: IDADEMAE é numérica real. Muitas mães jovens
    # (<20 anos) ou muito velhas (>35) têm risco elevado.
    # Verificar se alguma mãe era adolescente (risco obstétrico).

    # ── Escolaridade ──
    print(f"\n  Escolaridade da mãe:")
    esc_map = {1: "Nenhuma", 2: "1-3 anos", 3: "4-7 anos",
               4: "8-11 anos", 5: "12+ anos", 9: "Ignorado"}
    for _, row in df.iterrows():
        esc = row.get("ESCMAE", None)
        nome = row.get("NOME", "?")
        if pd.notna(esc) and esc != "Não informado":
            desc = esc_map.get(int(esc), f"Código {esc}")
            print(f"    {nome}: {desc}")
    # INTERPRETAÇÃO: Baixa escolaridade correlaciona com menor acesso
    # ao pré-natal de qualidade e menor capacidade de autogestão em saúde.

    # ── Local de ocorrência ──
    print(f"\n  Locais de ocorrência:")
    for loc, qtd in df["LOCAL DE OCORRENCIA"].value_counts().items():
        print(f"    {loc}: {qtd}")

    # ── Momento do óbito ──
    if "MOMENTO DO ÓBITO" in df.columns:
        print(f"\n  Momento do óbito:")
        for mom, qtd in df["MOMENTO DO ÓBITO"].value_counts().items():
            print(f"    {mom}: {qtd}")
    # INTERPRETAÇÃO: Tardio = até 42 dias pós-parto.
    # Indica que complicações pós-parto não estão sendo detectadas
    # ou tratadas a tempo.


# ═══════════════════════════════════════════════════════════════
#  2. ÓBITOS INFANTIL
# ═══════════════════════════════════════════════════════════════
def metricas_infantil():
    sep("2. ÓBITOS INFANTIL")
    df = carregar("infantil")

    # ── Total e distribuição mensal ──
    print(f"\n  Total de óbitos infantis: {len(df)}")
    print(f"\n  Distribuição por mês:")
    for mes, qtd in df["Mês Nome"].value_counts().sort_index().items():
        pct = (qtd / len(df)) * 100
        barra = "█" * int(pct / 2)
        print(f"    {mes:<10} {qtd:>3} ({pct:4.1f}%) {barra}")
    # INTERPRETAÇÃO: Maio é o pico (10 óbitos, 27%). Pode estar
    # associado a sazonalidade de doenças respiratórias (VSR, influenza)
    # que atingem neonatos com maior letalidade.

    # ── Distribuição por componente ──
    print(f"\n  Distribuição por componente (classificação etária):")
    comp_col = "COMPONENTE INFANTIL"
    if comp_col in df.columns:
        for comp, qtd in df[comp_col].value_counts().items():
            pct = (qtd / len(df)) * 100
            print(f"    {comp:<20} {qtd:>3} ({pct:4.1f}%)")
        # INTERPRETAÇÃO:
        # NEO PRECOCE (0-6 dias): causas relateadas ao parto e
        #   perinatalidade — asfixia, prematuridade, malformações.
        # NEO TARDIO (7-27 dias): infecções adquiridas no pós-parto,
        #   complicações de prematuridade.
        # PÓS NEONATAL (28+ dias): doenças infecciosas, respiratórias,
        #   sociais (violência, SIDS).
    else:
        print("    Coluna COMPONENTE INFANTIL não encontrada")

    # ── Peso ao nascer ──
    print(f"\n  Peso ao nascer (gramas):")
    peso_col = "PESO"
    if peso_col in df.columns:
        pesos = pd.to_numeric(df[peso_col], errors="coerce").dropna()
        pesos = pesos[pesos > 0]
        if len(pesos) > 0:
            print(f"    Média:   {pesos.mean():.0f}g")
            print(f"    Mediana: {pesos.median():.0f}g")
            print(f"    Mínimo:  {pesos.min():.0f}g")
            print(f"    Máximo:  {pesos.max():.0f}g")
            # Classificação OMS
            baixo = (pesos < 2500).sum()
            muito_baixo = (pesos < 1500).sum()
            normal = ((pesos >= 2500) & (pesos < 4000)).sum()
            alto = (pesos >= 4000).sum()
            print(f"\n    Classificação OMS:")
            print(f"      Muito baixo peso (<1500g):  {muito_baixo} ({muito_baixo/len(pesos)*100:.0f}%)")
            print(f"      Baixo peso (<2500g):         {baixo} ({baixo/len(pesos)*100:.0f}%)")
            print(f"      Peso normal (2500-3999g):    {normal} ({normal/len(pesos)*100:.0f}%)")
            print(f"      Peso alto (≥4000g):          {alto} ({alto/len(pesos)*100:.0f}%)")
            # INTERPRETAÇÃO: Baixo peso ao nascer (<2500g) é o principal
            # fator de risco para mortalidade neonatal. Neonatos com
            # <1500g têm risco 20-30x maior de óbito.

    # ── Causas principais ──
    print(f"\n  Principais causas (CB pós-investigação):")
    causa_col = "CB- PÓS INVESTIGAÇÃO"
    desc_col = "DESCRIÇÃO CB - PÓS INVESTIGAÇÃO"
    if causa_col in df.columns:
        causas = df[causa_col].dropna()
        causas = causas[causas != "Não informado"]
        if len(causas) > 0:
            for cid, qtd in causas.value_counts().head(8).items():
                # Buscar descrição
                desc = ""
                if desc_col in df.columns:
                    mask = df[causa_col] == cid
                    desc_vals = df.loc[mask, desc_col].dropna()
                    desc_vals = desc_vals[desc_vals != "Não informado"]
                    if len(desc_vals) > 0:
                        desc = f" — {desc_vals.iloc[0]}"
                print(f"    {cid}{desc}: {qtd} ({qtd/len(df)*100:.0f}%)")
        else:
            causa_col2 = "CB DO ORIGINAL"
            if causa_col2 in df.columns:
                causas = df[causa_col2].dropna()
                causas = causas[causas != "Não informado"]
                for cid, qtd in causas.value_counts().head(8).items():
                    print(f"    {cid}: {qtd} ({qtd/len(df)*100:.0f}%)")

    # ── Idade da mãe ──
    print(f"\n  Idade da mãe:")
    idades = pd.to_numeric(df["IDADEMAE"], errors="coerce").dropna()
    if len(idades) > 0:
        print(f"    Média: {idades.mean():.1f} anos")
        print(f"    Mínima: {idades.min():.0f} | Máxima: {idades.max():.0f}")
        adolescentes = (idades < 20).sum()
        adultas = ((idades >= 20) & (idades < 35)).sum()
        idosa = (idades >= 35).sum()
        print(f"    Adolescentes (<20): {adolescentes} ({adolescentes/len(idades)*100:.0f}%)")
        print(f"    Adultas (20-34):    {adultas} ({adultas/len(idades)*100:.0f}%)")
        print(f"    Idosas (≥35):       {idosa} ({idosa/len(idades)*100:.0f}%)")
    # INTERPRETAÇÃO: Mães adolescentes têm maior risco de prematuridade
    # e baixo peso. Mães >35 anos associadas a complicações gestacionais.


# ═══════════════════════════════════════════════════════════════
#  3. ÓBITOS FETAIS
# ═══════════════════════════════════════════════════════════════
def metricas_fetal():
    sep("3. ÓBITOS FETAIS")
    df = carregar("fetal")

    # ── Total e distribuição mensal ──
    print(f"\n  Total de óbitos fetais: {len(df)}")
    print(f"\n  Distribuição por mês:")
    for mes, qtd in df["Mês Nome"].value_counts().sort_index().items():
        pct = (qtd / len(df)) * 100
        barra = "█" * int(pct / 2)
        print(f"    {mes:<10} {qtd:>3} ({pct:4.1f}%) {barra}")
    # INTERPRETAÇÃO: Óbitos fetais (natimortos) representam fetos que
    # nasceram sem vida ≥22 semanas. Febreiro e janeiro concentram
    # os maiores picos (30% cada) — correlação com gestantes que
    # iniciaram pré-natal tardiamente.

    # ── Principais causas (pós-investigação) ──
    print(f"\n  Principais causas (CB pós-investigação):")
    causa_col = "CB PÓS INVEST"
    desc_col = "DESCRIÇÃO CB - PÓS INVESTIGAÇÃO"
    if causa_col in df.columns:
        causas = df[causa_col].dropna()
        causas = causas[causas != "Não informado"]
        if len(causas) > 0:
            for cid, qtd in causas.value_counts().head(8).items():
                desc = ""
                if desc_col in df.columns:
                    mask = df[causa_col] == cid
                    desc_vals = df.loc[mask, desc_col].dropna()
                    desc_vals = desc_vals[desc_vals != "Não informado"]
                    if len(desc_vals) > 0:
                        desc = f" — {desc_vals.iloc[0]}"
                print(f"    {cid}{desc}: {qtd} ({qtd/len(df)*100:.0f}%)")
    # INTERPRETAÇÃO: P20.9 (hipóxia intra-uterina) como causa líder
    # indica sofrimento fetal não detectado ou mal gerenciado.
    # P02.1 (descolamento placentário) sugere falha no monitoramento
    # de gestantes de alto risco.

    # ── Causa original vs pós-investigação (discrepâncias) ──
    print(f"\n  Discrepância original vs pós-investigação:")
    orig_col = "CB- DO ORIGINAL"
    if orig_col in df.columns and causa_col in df.columns:
        comp = df[[orig_col, causa_col]].dropna()
        comp = comp[comp[orig_col] != "Não informado"]
        comp = comp[comp[causa_col] != "Não informado"]
        alteradas = comp[comp[orig_col] != comp[causa_col]]
        print(f"    Casos com causa alterada: {len(alteradas)}/{len(comp)} ({len(alteradas)/max(len(comp),1)*100:.0f}%)")
        for _, row in alteradas.iterrows():
            print(f"      {row[orig_col]} → {row[causa_col]}")
    # INTERPRETAÇÃO: Alteração na causa indica que a investigação
    # epidemiológica está funcionando — detectando causas reais que
    # o atestado inicial não captou. Quanto maior a discrepância,
    # mais necessária é a investigação.

    # ── Escolaridade da mãe ──
    print(f"\n  Escolaridade da mãe (ESCMAE):")
    esc_map = {1: "Nenhuma", 2: "1-3 anos", 3: "4-7 anos",
               4: "8-11 anos", 5: "12+ anos", 9: "Ignorado"}
    if "ESCMAE" in df.columns:
        esc_vals = df["ESCMAE"].dropna()
        esc_vals = esc_vals[esc_vals != "Não informado"]
        if len(esc_vals) > 0:
            for esc, qtd in esc_vals.value_counts().sort_index().items():
                desc = esc_map.get(int(esc), f"Código {esc}") if esc != "Não informado" else esc
                print(f"    {desc}: {qtd} ({qtd/len(esc_vals)*100:.0f}%)")
        # INTERPRETAÇÃO: Mães com baixa escolaridade (<8 anos estudo)
        # tendem a ter menor adesão ao pré-natal e menor capacidade
        # de identificar sinais de alerta na gestação.

    # ESCMAE2010 (classificação atualizada)
    if "ESCMAE2010" in df.columns:
        print(f"\n  Escolaridade (ESCMAE2010 - nova classificação):")
        esc10_map = {0: "Sem instrução", 1: "Fund. incompleto", 2: "Fund. completo",
                     3: "Médio incompleto", 4: "Médio completo", 5: "Superior",
                     9: "Ignorado"}
        esc10 = df["ESCMAE2010"].dropna()
        esc10 = esc10[esc10 != "Não informado"]
        if len(esc10) > 0:
            for esc, qtd in esc10.value_counts().sort_index().items():
                desc = esc10_map.get(int(esc), f"Código {esc}")
                print(f"    {desc}: {qtd} ({qtd/len(esc10)*100:.0f}%)")

    # ── Idade da mãe ──
    print(f"\n  Idade da mãe:")
    idades = pd.to_numeric(df["IDADEMAE"], errors="coerce").dropna()
    if len(idades) > 0:
        print(f"    Média: {idades.mean():.1f} anos")
        print(f"    Mínima: {idades.min():.0f} | Máxima: {idades.max():.0f}")

    # ── Semanas de gestação ──
    print(f"\n  Semanas de gestação:")
    sem_cols = ["SEMAGESTAC", "GESTACAO"]
    for col in sem_cols:
        if col in df.columns:
            sems = pd.to_numeric(df[col], errors="coerce").dropna()
            sems = sems[sems > 0]
            if len(sems) > 0:
                print(f"    ({col}) Média: {sems.mean():.1f} semanas")
                prematuro = (sems < 37).sum()
                termo = ((sems >= 37) & (sems <= 41)).sum()
                pos_termo = (sems > 41).sum()
                print(f"    Prematuro (<37 sem):   {prematuro} ({prematuro/len(sems)*100:.0f}%)")
                print(f"    Termo (37-41 sem):     {termo} ({termo/len(sems)*100:.0f}%)")
                print(f"    Pós-termo (>41 sem):   {pos_termo} ({pos_termo/len(sems)*100:.0f}%)")
                break
    # INTERPRETAÇÃO: Prematuridade é fator de risco independente.
    # Fetos com <32 semanas têm taxas muito altas de natimortalidade.

    # ── Peso ao nascer ──
    print(f"\n  Peso ao nascer (fetais):")
    if "PESO" in df.columns:
        pesos = pd.to_numeric(df["PESO"], errors="coerce").dropna()
        pesos = pesos[pesos > 0]
        if len(pesos) > 0:
            print(f"    Média:   {pesos.mean():.0f}g")
            print(f"    Mínimo:  {pesos.min():.0f}g")
            print(f"    Máximo:  {pesos.max():.0f}g")
            baixo = (pesos < 2500).sum()
            print(f"    Baixo peso (<2500g): {baixo} ({baixo/len(pesos)*100:.0f}%)")

    # ── Local de ocorrência ──
    print(f"\n  Locais de ocorrência:")
    for loc, qtd in df["LOCAL DE OCORRENCIA"].value_counts().items():
        print(f"    {loc}: {qtd} ({qtd/len(df)*100:.0f}%)")
    # INTERPRETAÇÃO: Concentração em poucos hospitais indica que
    # intervenções nestas unidades terão impacto direto nos números.


# ═══════════════════════════════════════════════════════════════
#  RESUMO EXECUTIVO
# ═══════════════════════════════════════════════════════════════
def resumo_executivo():
    sep("RESUMO EXECUTIVO PARA APRESENTAÇÃO")

    materno = carregar("materno")
    fetal = carregar("fetal")
    infantil = carregar("infantil")
    total = len(materno) + len(fetal) + len(infantil)

    print(f"\n  Total geral: {total} óbitos")
    print(f"    Materno:  {len(materno):>3} ({len(materno)/total*100:.1f}%)")
    print(f"    Fetal:    {len(fetal):>3} ({len(fetal)/total*100:.1f}%)")
    print(f"    Infantil: {len(infantil):>3} ({len(infantil)/total*100:.1f}%)")

    # Métricas-chave para slides
    print(f"\n  ── Métricas-chave para apresentação ──")

    # Mês com mais óbitos
    todos = pd.concat([materno, fetal, infantil], ignore_index=True)
    if "Mês Nome" in todos.columns:
        mes_max = todos["Mês Nome"].value_counts().idxmax()
        qtd_max = todos["Mês Nome"].value_counts().max()
        print(f"  • Mês mais crítico: {mes_max} ({qtd_max} óbitos)")

    # Hospital principal
    if "LOCAL DE OCORRENCIA" in todos.columns:
        loc_max = todos["LOCAL DE OCORRENCIA"].value_counts().idxmax()
        qtd_loc = todos["LOCAL DE OCORRENCIA"].value_counts().max()
        print(f"  • Hospital principal: {loc_max} ({qtd_loc} óbitos)")

    # Causa fetal líder
    causa_fetal_col = "CB PÓS INVEST"
    if causa_fetal_col in fetal.columns:
        causas_f = fetal[causa_fetal_col].dropna()
        causas_f = causas_f[causas_f != "Não informado"]
        if len(causas_f) > 0:
            cid_lider = causas_f.value_counts().idxmax()
            qtd_cid = causas_f.value_counts().max()
            print(f"  • Causa fetal líder: {cid_lider} ({qtd_cid} casos)")

    # Componente infantil líder
    comp_col = "COMPONENTE INFANTIL"
    if comp_col in infantil.columns:
        comp_max = infantil[comp_col].value_counts().idxmax()
        qtd_comp = infantil[comp_col].value_counts().max()
        print(f"  • Componente infantil líder: {comp_max} ({qtd_comp} casos)")

    print()


# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "█"*60)
    print("  MÉTRICAS — APRESENTAÇÃO ÓBITOS SANTA CRUZ/RJ 2026")
    print("█"*60)

    metricas_materno()
    metricas_infantil()
    metricas_fetal()
    resumo_executivo()

    print("  Concluído.\n")
