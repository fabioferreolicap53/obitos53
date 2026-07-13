"""
Geração de Gráficos — Óbitos Santa Cruz/RJ 2026
Matplotlib + Seaborn | Paleta azul/cinza/coral
Salva PNGs em pasta 'graficos'
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from pathlib import Path

# ─── Configuração ───────────────────────────────────────────────
SEPARADOR = ";"
ENCODING = "utf-8-sig"
PASTA_DADOS = Path("dados_limpos")
PASTA_GRAF = Path("graficos")
PASTA_GRAF.mkdir(exist_ok=True)

# Paleta customizada
CORES = {
    "azul_escuro":  "#1e3a5f",
    "azul":         "#3b82f6",
    "azul_claro":   "#93c5fd",
    "cinza":        "#94a3b8",
    "cinza_claro":  "#e2e8f0",
    "coral":        "#f97066",
    "coral_claro":  "#fca5a1",
    "verde":        "#22c55e",
    "amarelo":      "#eab308",
    "roxo":         "#a78bfa",
}

PALETA_BARRAS = [CORES["azul"], CORES["coral"], CORES["verde"],
                 CORES["amarelo"], CORES["roxo"]]

# Estilo global
sns.set_theme(style="whitegrid", font_scale=1.1)
plt.rcParams.update({
    "figure.facecolor": "#0f172a",
    "axes.facecolor":   "#0f172a",
    "axes.edgecolor":   "#334155",
    "axes.labelcolor":  "#e2e8f0",
    "xtick.color":      "#94a3b8",
    "ytick.color":      "#94a3b8",
    "text.color":       "#f8fafc",
    "grid.color":       "#1e293b",
    "grid.alpha":       0.5,
    "font.family":      "sans-serif",
    "savefig.dpi":      200,
    "savefig.bbox":     "tight",
    "savefig.facecolor": "#0f172a",
})


def carregar(nome: str) -> pd.DataFrame:
    return pd.read_csv(PASTA_DADOS / f"{nome}_limpo.csv",
                       sep=SEPARADOR, encoding=ENCODING, low_memory=False)


def salvar(fig, nome: str):
    caminho = PASTA_GRAF / f"{nome}.png"
    fig.savefig(caminho, dpi=200, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    print(f"  Salvo: {caminho}")


# ═══════════════════════════════════════════════════════════════
#  1. EVOLUÇÃO TEMPORAL — 3 tipos de óbitos (subplot)
# ═══════════════════════════════════════════════════════════════
def grafico_evolucao_temporal():
    print("\n  [1/3] Evolução temporal...")
    materno = carregar("materno")
    fetal = carregar("fetal")
    infantil = carregar("infantil")

    bases = {"Materno": materno, "Fetal": fetal, "Infantil": infantil}
    meses_pt = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun"}

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    fig.suptitle("Evolução Mensal dos Óbitos — Santa Cruz/RJ 2026",
                 fontsize=16, fontweight="bold", y=0.98, color="#f8fafc")

    titulos = ["Óbitos Maternos", "Óbitos Fetais", "Óbitos Infantil"]
    cores_linha = [CORES["coral"], CORES["azul"], CORES["roxo"]]
    cores_area = [CORES["coral_claro"], CORES["azul_claro"], "#c4b5fd"]

    for ax, (nome, df), titulo, cor, cor_area in zip(
        axes, bases.items(), titulos, cores_linha, cores_area
    ):
        contagem = df["Mês"].value_counts().sort_index()
        meses_idx = sorted(contagem.index)
        meses_label = [meses_pt.get(m, str(m)) for m in meses_idx]
        valores = [contagem.get(m, 0) for m in meses_idx]

        # Área preenchida
        ax.fill_between(range(len(meses_idx)), valores,
                        alpha=0.15, color=cor_area)
        # Linha com marcadores
        ax.plot(range(len(meses_idx)), valores,
                color=cor, linewidth=2.5, marker="o", markersize=8,
                markerfacecolor=cor, markeredgecolor="#0f172a",
                markeredgewidth=2, zorder=5)
        # Valores nos pontos
        for i, v in enumerate(valores):
            if v > 0:
                ax.annotate(str(v), (i, v), textcoords="offset points",
                           xytext=(0, 12), ha="center", fontsize=11,
                           fontweight="bold", color=cor)

        ax.set_title(f"{titulo} (n={len(df)})", fontsize=13,
                     fontweight="bold", color=cor, pad=8)
        ax.set_ylabel("Óbitos", fontsize=10, color="#94a3b8")
        ax.set_ylim(bottom=0)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.grid(True, alpha=0.3)

    axes[-1].set_xticks(range(len(meses_idx)))
    axes[-1].set_xticklabels(meses_label, fontsize=11)
    axes[-1].set_xlabel("Mês de Ocorrência", fontsize=11, color="#94a3b8")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    salvar(fig, "01_evolucao_temporal")


# ═══════════════════════════════════════════════════════════════
#  2. CAUSAS MATERNO — Barras horizontais top 5
# ═══════════════════════════════════════════════════════════════
def grafico_causas_materno():
    print("\n  [2/3] Causas materno...")
    df = carregar("materno")

    # CID mapping para nomes legíveis
    cid_nomes = {
        "J189": "Pneumonia (J18.9)",
        "I249": "Isquemia Aguda do Coração (I24.9)",
        "N179": "Insuficiência Renal Aguda (N17.9)",
        "O961": "Causa Materna Tardia (O96.1)",
        "I499": "Arritmia Cardíaca (I49.9)",
        "I509": "Insuficiência Cardíaca (I50.9)",
        "G936": "Edema Cerebral (G93.6)",
        "K920": "Hematêmese (K92.0)",
        "O266": "Complic. Gravidez (O26.6)",
        "O244": "Diabetes Gestacional (O24.4)",
        "I10":  "Hipertensão (I10)",
        "E669": "Obesidade (E66.9)",
        "J189": "Pneumonia (J18.9)",
    }

    # Combinar CAUSABAS e LINHAA para causas
    causa_col = "CAUSABAS"
    linh_a_col = "LINHAA"

    # Usar CAUSABAS como causa básica
    causas = df[causa_col].dropna().value_counts().head(5)

    # Mapear nomes
    labels = []
    for cid in causas.index:
        nome = cid_nomes.get(cid, cid)
        labels.append(nome)

    valores = causas.values.tolist()

    # Inverter para barras horizontais (maior em cima)
    labels = labels[::-1]
    valores = valores[::-1]

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.suptitle("Principais Causas de Óbito Materno — Pós-Investigação",
                 fontsize=15, fontweight="bold", y=0.98, color="#f8fafc")

    # Barras com gradiente
    barras = ax.barh(range(len(labels)), valores,
                     color=[CORES["coral"] if i == len(labels)-1
                            else CORES["azul"]
                            for i in range(len(labels))],
                     edgecolor="#0f172a", linewidth=1.5, height=0.6)

    # Valores nas barras
    for bar, val in zip(barras, valores):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                f" {val}", va="center", fontsize=12, fontweight="bold",
                color="#f8fafc")

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=11, color="#e2e8f0")
    ax.set_xlabel("Número de Óbitos", fontsize=11, color="#94a3b8")
    ax.set_xlim(0, max(valores) * 1.4)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.grid(True, axis="x", alpha=0.2)

    # Nota
    ax.text(0.98, 0.02,
            f"n={len(df)} óbitos maternos | CID-10 pós-GT Comissão",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=9, color="#64748b", style="italic")

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    salvar(fig, "02_causas_materno")


# ═══════════════════════════════════════════════════════════════
#  3. DISTRIBUIÇÃO INFANTIL — Donut por componente
# ═══════════════════════════════════════════════════════════════
def grafico_distribuicao_infantil():
    print("\n  [3/3] Distribuição infantil...")
    df = carregar("infantil")

    comp_col = "COMPONENTE INFANTIL"
    contagem = df[comp_col].value_counts()

    # Mapear para labels limpos
    label_map = {
        "NEO PRECOCE":  "Neonatal Precoce\n(0-6 dias)",
        "NEO TARDIO":   "Neonatal Tardio\n(7-27 dias)",
        "PÓS NEONATAL": "Pós-Neonatal\n(28+ dias)",
    }
    cores_map = {
        "NEO PRECOCE":  CORES["coral"],
        "NEO TARDIO":   CORES["azul"],
        "PÓS NEONATAL": CORES["roxo"],
    }

    labels = [label_map.get(c, c) for c in contagem.index]
    valores = contagem.values
    cores = [cores_map.get(c, CORES["cinza"]) for c in contagem.index]
    total = valores.sum()

    fig, (ax_bar, ax_donut) = plt.subplots(1, 2, figsize=(14, 6),
                                            gridspec_kw={"width_ratios": [1, 1.2]})
    fig.suptitle("Distribuição de Óbitos Infantis por Faixa Etária",
                 fontsize=15, fontweight="bold", y=0.98, color="#f8fafc")

    # ── Donut (rosca) ──
    wedges, texts, autotexts = ax_donut.pie(
        valores, labels=None, autopct=lambda p: f"{p:.0f}%",
        colors=cores, startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.45, edgecolor="#0f172a", linewidth=2.5),
    )
    for t in autotexts:
        t.set_fontsize(13)
        t.set_fontweight("bold")
        t.set_color("#f8fafc")

    # Centro
    ax_donut.text(0, 0.05, str(total), ha="center", va="center",
                  fontsize=32, fontweight="bold", color="#f8fafc")
    ax_donut.text(0, -0.15, "óbitos", ha="center", va="center",
                  fontsize=11, color="#94a3b8")

    # Legenda
    legend_labels = [f"{label_map.get(c, c)}  ({v})" for c, v in
                     zip(contagem.index, valores)]
    ax_donut.legend(wedges, legend_labels, loc="center left",
                    bbox_to_anchor=(0.95, 0.5), fontsize=10,
                    frameon=False, labelcolor="#e2e8f0")

    # ── Barras horizontais complementares ──
    y_pos = range(len(labels))
    barras = ax_bar.barh(y_pos, valores, color=cores,
                         edgecolor="#0f172a", linewidth=1.5, height=0.55)

    for bar, val, pct in zip(barras, valores, (valores/total*100)):
        ax_bar.text(bar.get_width() + 0.3,
                    bar.get_y() + bar.get_height()/2,
                    f"{val}  ({pct:.0f}%)",
                    va="center", fontsize=12, fontweight="bold",
                    color="#f8fafc")

    ax_bar.set_yticks(y_pos)
    ax_bar.set_yticklabels(labels, fontsize=11, color="#e2e8f0")
    ax_bar.set_xlabel("Número de Óbitos", fontsize=11, color="#94a3b8")
    ax_bar.set_xlim(0, max(valores) * 1.5)
    ax_bar.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax_bar.grid(True, axis="x", alpha=0.2)
    ax_bar.invert_yaxis()

    # Nota
    ax_bar.text(0.98, 0.02,
                "Neo precoce = parto+6d | Tardio = 7-27d | Pós-neonatal = 28d+",
                transform=ax_bar.transAxes, ha="right", va="bottom",
                fontsize=8, color="#64748b", style="italic")

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    salvar(fig, "03_distribuicao_infantil")


# ═══════════════════════════════════════════════════════════════
#  BÔNUS: Dashboard resumo
# ═══════════════════════════════════════════════════════════════
def grafico_dashboard_resumo():
    print("\n  [BÔNUS] Dashboard resumo...")
    materno = carregar("materno")
    fetal = carregar("fetal")
    infantil = carregar("infantil")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Dashboard Resumo — Óbitos Santa Cruz/RJ 2026",
                 fontsize=17, fontweight="bold", y=0.98, color="#f8fafc")

    meses_pt = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun"}

    # ── [0,0] Total por tipo ──
    ax = axes[0, 0]
    tipos = ["Materno", "Fetal", "Infantil"]
    totais = [len(materno), len(fetal), len(infantil)]
    cores_tipos = [CORES["coral"], CORES["azul"], CORES["roxo"]]
    barras = ax.bar(tipos, totais, color=cores_tipos,
                    edgecolor="#0f172a", linewidth=1.5, width=0.55)
    for bar, val in zip(barras, totais):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                str(val), ha="center", fontsize=14, fontweight="bold",
                color="#f8fafc")
    ax.set_title("Total por Tipo", fontsize=12, fontweight="bold",
                 color="#93c5fd", pad=10)
    ax.set_ylabel("Óbitos")
    ax.set_ylim(0, max(totais) * 1.2)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # ── [0,1] Evolução mensal empilhada ──
    ax = axes[0, 1]
    todos = pd.concat([materno, fetal, infantil], ignore_index=True)
    meses_ordenados = sorted(todos["Mês"].dropna().unique())
    for tipo, cor, df_base in [("Materno", CORES["coral"], materno),
                                ("Fetal", CORES["azul"], fetal),
                                ("Infantil", CORES["roxo"], infantil)]:
        contagem = df_base["Mês"].value_counts().sort_index()
        vals = [contagem.get(m, 0) for m in meses_ordenados]
        ax.plot([meses_pt.get(m, m) for m in meses_ordenados], vals,
                marker="o", linewidth=2, markersize=6, label=tipo, color=cor)
    ax.set_title("Evolução Mensal", fontsize=12, fontweight="bold",
                 color="#93c5fd", pad=10)
    ax.set_ylabel("Óbitos")
    ax.legend(fontsize=9, frameon=False, labelcolor="#e2e8f0")
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    # ── [1,0] Top 5 hospitais ──
    ax = axes[1, 0]
    loc_col = "LOCAL DE OCORRENCIA"
    top_locs = todos[loc_col].value_counts().head(5)
    labels_hosp = [l[:30] + "..." if len(l) > 30 else l for l in top_locs.index]
    vals_hosp = top_locs.values
    barras = ax.barh(range(len(labels_hosp)), vals_hosp,
                     color=PALETA_BARRAS[:len(labels_hosp)],
                     edgecolor="#0f172a", linewidth=1, height=0.55)
    for bar, val in zip(barras, vals_hosp):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(val), va="center", fontsize=11, fontweight="bold",
                color="#f8fafc")
    ax.set_yticks(range(len(labels_hosp)))
    ax.set_yticklabels(labels_hosp, fontsize=9, color="#e2e8f0")
    ax.set_title("Top 5 Hospitais", fontsize=12, fontweight="bold",
                 color="#93c5fd", pad=10)
    ax.set_xlabel("Óbitos")
    ax.invert_yaxis()

    # ── [1,1] Donut tipos ──
    ax = axes[1, 1]
    wedges, texts, autotexts = ax.pie(
        totais, labels=tipos, autopct="%1.0f%%",
        colors=cores_tipos, startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.4, edgecolor="#0f172a", linewidth=2),
        textprops=dict(color="#e2e8f0", fontsize=11),
    )
    for t in autotexts:
        t.set_fontsize(12)
        t.set_fontweight("bold")
        t.set_color("#f8fafc")
    ax.set_title("Composição", fontsize=12, fontweight="bold",
                 color="#93c5fd", pad=10)

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    salvar(fig, "04_dashboard_resumo")


# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "█"*60)
    print("  GERAÇÃO DE GRÁFICOS — ÓBITOS SANTA CRUZ/RJ 2026")
    print("█"*60)

    grafico_evolucao_temporal()
    grafico_causas_materno()
    grafico_distribuicao_infantil()
    grafico_dashboard_resumo()

    print(f"\n  Todos os gráficos salvos em: {PASTA_GRAF.resolve()}")
    print("  Concluído.\n")
