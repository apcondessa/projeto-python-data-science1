"""Dashboard de Salários na Área de Dados.

Análise interativa de ~133 mil registros salariais de profissionais de dados
(2020–2025), com filtros, KPIs, tendências e comparação entre cargos e países.
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ---------------------------------------------------------------------------
# Configuração da página e identidade visual
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
ARQUIVO_DADOS = BASE_DIR / "dados-imersao-final.csv"
ARQUIVO_README = BASE_DIR / "README.md"

# Paleta categórica (cores distintas e legíveis sobre fundo escuro)
PALETA = ["#7C5CFF", "#00D4B8", "#FF6B9A", "#FFB547", "#4DA3FF", "#A3E635"]
ESCALA_CONTINUA = ["#2A2F6B", "#4B3FB0", "#7C5CFF", "#00A7C4", "#00D4B8", "#B8F5E8"]

pio.templates["dados"] = go.layout.Template(pio.templates["plotly_dark"])
pio.templates["dados"].layout.update(
    colorway=PALETA,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, Segoe UI, sans-serif", size=13, color="#E8EAF6"),
    title=dict(font=dict(size=16, color="#FFFFFF"), x=0.02, xanchor="left"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.07)", zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#1A1F3D", bordercolor="#7C5CFF", font_color="#FFFFFF"),
    margin=dict(l=10, r=10, t=50, b=10),
)
pio.templates.default = "dados"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }

    .hero {
        background: linear-gradient(120deg, #7C5CFF 0%, #4DA3FF 45%, #00D4B8 100%);
        border-radius: 18px; padding: 28px 32px; margin-bottom: 1.4rem;
        box-shadow: 0 10px 30px rgba(124, 92, 255, 0.25);
    }
    .hero h1 { color: #FFFFFF; font-weight: 800; font-size: 2.1rem; margin: 0; padding: 0; }
    .hero p  { color: rgba(255,255,255,0.92); font-size: 1.02rem; margin: 6px 0 0 0; }

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #1A1F3D, #232A55);
        border: 1px solid #2E3670; border-left: 5px solid var(--accent, #7C5CFF);
        border-radius: 14px; padding: 16px 20px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.25);
    }
    [data-testid="stMetricLabel"] p { color: #A9B0D6; font-weight: 600; }
    [data-testid="stMetricValue"], [data-testid="stMetricValue"] > div {
        color: #FFFFFF !important; font-weight: 800 !important; font-size: 1.55rem !important;
        white-space: normal !important; overflow: visible !important; line-height: 1.25 !important;
    }
    [data-testid="stColumn"]:nth-of-type(1) [data-testid="stMetric"] { --accent: #7C5CFF; }
    [data-testid="stColumn"]:nth-of-type(2) [data-testid="stMetric"] { --accent: #00D4B8; }
    [data-testid="stColumn"]:nth-of-type(3) [data-testid="stMetric"] { --accent: #FF6B9A; }
    [data-testid="stColumn"]:nth-of-type(4) [data-testid="stMetric"] { --accent: #FFB547; }

    .insight {
        background: #1A1F3D; border: 1px solid #2E3670; border-radius: 14px;
        padding: 14px 18px; min-height: 84px;
    }
    .insight b { color: #00D4B8; }

    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #141833, #0F1226); }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background: #1A1F3D; border-radius: 10px 10px 0 0; padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] { background: #7C5CFF !important; color: #FFFFFF !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------
ROTULOS = {
    "senioridade": {"junior": "Júnior", "pleno": "Pleno", "senior": "Sênior", "executivo": "Executivo"},
    "contrato": {"integral": "Integral", "parcial": "Parcial", "contrato": "Contrato", "freelancer": "Freelancer"},
    "remoto": {"presencial": "Presencial", "hibrido": "Híbrido", "remoto": "Remoto"},
    "tamanho_empresa": {"pequena": "Pequena", "media": "Média", "grande": "Grande"},
}
ORDEM = {
    "senioridade": ["Júnior", "Pleno", "Sênior", "Executivo"],
    "contrato": ["Integral", "Parcial", "Contrato", "Freelancer"],
    "remoto": ["Presencial", "Híbrido", "Remoto"],
    "tamanho_empresa": ["Pequena", "Média", "Grande"],
}
MIN_AMOSTRA = 30  # mínimo de registros para um grupo entrar nos rankings


@st.cache_data(show_spinner="Carregando dados…")
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv(ARQUIVO_DADOS)
    df = df.dropna(subset=["usd"])
    for coluna, mapa in ROTULOS.items():
        df[coluna] = df[coluna].map(mapa).fillna(df[coluna])
    return df


def usd(valor: float) -> str:
    return f"US$ {valor / 1000:,.0f} mil".replace(",", ".")


df = carregar_dados()

# ---------------------------------------------------------------------------
# Filtros (barra lateral)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🔍 Filtros")
    anos = sorted(df["ano"].unique().tolist())
    ano_ini, ano_fim = st.select_slider("Período", options=anos, value=(anos[0], anos[-1]))

    def filtro(rotulo: str, coluna: str) -> list:
        opcoes = ORDEM.get(coluna, sorted(df[coluna].unique()))
        return st.multiselect(rotulo, opcoes, default=opcoes)

    sel_sen = filtro("Senioridade", "senioridade")
    sel_rem = filtro("Modelo de trabalho", "remoto")
    sel_con = filtro("Tipo de contrato", "contrato")
    sel_tam = filtro("Tamanho da empresa", "tamanho_empresa")

    st.markdown("---")
    st.caption(
        f"Fonte: pesquisa global de salários na área de dados, {anos[0]}–{anos[-1]}. "
        "Valores anuais convertidos para USD. Detalhes na aba **Sobre o projeto**."
    )

df_f = df[
    df["ano"].between(ano_ini, ano_fim)
    & df["senioridade"].isin(sel_sen)
    & df["remoto"].isin(sel_rem)
    & df["contrato"].isin(sel_con)
    & df["tamanho_empresa"].isin(sel_tam)
]

# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
      <h1>📊 Salários na Área de Dados</h1>
      <p>Quanto ganham profissionais de dados no mundo: por cargo, senioridade, modelo de trabalho e país
      ({ano_ini}–{ano_fim}).</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if df_f.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
mediana = df_f["usd"].median()
p25, p75 = df_f["usd"].quantile([0.25, 0.75])

ano_ref = int(df_f["ano"].max())
anterior = df_f.loc[df_f["ano"] == ano_ref - 1, "usd"]
atual = df_f.loc[df_f["ano"] == ano_ref, "usd"]
delta = None
if len(anterior) >= MIN_AMOSTRA and len(atual) >= MIN_AMOSTRA:
    delta = f"{atual.median() / anterior.median() - 1:+.1%} vs {ano_ref - 1}"

cargos_validos = df_f.groupby("cargo")["usd"].agg(["median", "size"]).query("size >= @MIN_AMOSTRA")
cargo_top = cargos_validos["median"].idxmax() if not cargos_validos.empty else "—"

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salário mediano anual", usd(mediana), delta,
          help=f"Mediana anual em USD. A variação compara {ano_ref} com {ano_ref - 1}.")
c2.metric("Faixa central (P25–P75)", f"US$ {p25 / 1000:.0f}–{p75 / 1000:.0f} mil",
          help="Metade dos profissionais ganha dentro desta faixa.")
c3.metric("Registros analisados", f"{len(df_f):,}".replace(",", "."))
c4.metric("Cargo mais bem pago", cargo_top,
          help=f"Maior mediana entre cargos com pelo menos {MIN_AMOSTRA} registros.")

# Destaques calculados a partir dos filtros
sen_med = df_f.groupby("senioridade")["usd"].median()
rem = df_f.groupby("remoto")["usd"].agg(["median", "size"]).query("size >= @MIN_AMOSTRA")["median"]
insights = []
if {"Júnior", "Sênior"} <= set(sen_med.index):
    insights.append(f"Um profissional <b>Sênior</b> ganha, em mediana, "
                    f"<b>{sen_med['Sênior'] / sen_med['Júnior']:.1f}×</b> o salário de um <b>Júnior</b>.")
if {"Remoto", "Presencial"} <= set(rem.index):
    insights.append(f"Vagas <b>remotas</b> pagam <b>{rem['Remoto'] / rem['Presencial'] - 1:+.0%}</b> "
                    f"em relação às <b>presenciais</b> (mediana).")
participacao_eua = (df_f["residencia"] == "US").mean()
insights.append(f"<b>{participacao_eua:.0%}</b> dos registros são de profissionais residentes nos "
                f"<b>EUA</b>: compare países com cautela.")

st.markdown("#### 💡 Destaques")
for col, texto in zip(st.columns(len(insights)), insights):
    col.markdown(f'<div class="insight">{texto}</div>', unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------------------------
# Abas de análise
# ---------------------------------------------------------------------------
aba_geral, aba_cargos, aba_perfil, aba_geo, aba_dados, aba_sobre = st.tabs(
    ["📈 Visão geral", "💼 Cargos", "🧭 Perfil & trabalho", "🌍 Geografia", "🗂️ Dados", "ℹ️ Sobre o projeto"]
)

with aba_geral:
    g1, g2 = st.columns(2)
    with g1:
        tendencia = (df_f.groupby(["ano", "senioridade"])["usd"]
                     .agg(mediana="median", registros="size").reset_index()
                     .query("registros >= @MIN_AMOSTRA"))
        fig = px.line(
            tendencia, x="ano", y="mediana", color="senioridade", markers=True,
            category_orders={"senioridade": ORDEM["senioridade"]},
            hover_data={"registros": True},
            title="Evolução do salário mediano por senioridade",
            labels={"mediana": "Mediana anual (USD)", "ano": "", "senioridade": "Senioridade"},
        )
        fig.update_traces(line_width=3, marker_size=8)
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Pontos com menos de {MIN_AMOSTRA} registros foram omitidos.")
    with g2:
        fig = px.histogram(
            df_f, x="usd", nbins=40, title="Distribuição dos salários anuais",
            labels={"usd": "Salário anual (USD)"}, color_discrete_sequence=["#00D4B8"],
        )
        fig.add_vline(x=mediana, line_dash="dash", line_color="#FFB547",
                      annotation_text=f"Mediana {usd(mediana)}", annotation_font_color="#FFB547")
        fig.update_layout(yaxis_title="Profissionais", bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

with aba_cargos:
    st.caption(f"Somente cargos com pelo menos {MIN_AMOSTRA} registros, para evitar distorções de amostras pequenas.")
    top_n = st.slider("Quantidade de cargos", 5, 20, 10)
    ranking = (df_f.groupby("cargo")["usd"].agg(mediana="median", registros="size")
               .query("registros >= @MIN_AMOSTRA").nlargest(top_n, "mediana")
               .sort_values("mediana").reset_index())
    altura = max(400, 34 * top_n)
    g1, g2 = st.columns([3, 2])
    with g1:
        fig = px.bar(
            ranking, x="mediana", y="cargo", orientation="h",
            color="mediana", color_continuous_scale=ESCALA_CONTINUA,
            text=ranking["mediana"].map(usd), hover_data={"registros": True},
            title=f"Top {top_n} cargos por salário mediano",
            labels={"mediana": "Mediana anual (USD)", "cargo": ""},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_xaxes(range=[0, ranking["mediana"].max() * 1.22])
        fig.update_layout(coloraxis_showscale=False, height=altura)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        populares = df_f["cargo"].value_counts().head(8).index
        fig = px.box(
            df_f[df_f["cargo"].isin(populares)], x="usd", y="cargo", color="cargo", points=False,
            title="Dispersão salarial dos 8 cargos mais comuns",
            labels={"usd": "Salário anual (USD)", "cargo": ""},
        )
        fig.update_layout(showlegend=False, height=altura)
        st.plotly_chart(fig, use_container_width=True)

with aba_perfil:
    g1, g2 = st.columns(2)
    with g1:
        fig = px.box(
            df_f, x="senioridade", y="usd", color="senioridade", points=False,
            category_orders={"senioridade": ORDEM["senioridade"]},
            title="Salário por senioridade",
            labels={"usd": "Salário anual (USD)", "senioridade": ""},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        modelo = df_f.groupby(["senioridade", "remoto"]).size().reset_index(name="registros")
        modelo["pct"] = modelo["registros"] / modelo.groupby("senioridade")["registros"].transform("sum")
        fig = px.bar(
            modelo, x="senioridade", y="pct", color="remoto", barmode="stack",
            text=modelo["pct"].map(lambda v: f"{v:.0%}" if v >= 0.03 else ""),
            category_orders={"senioridade": ORDEM["senioridade"], "remoto": ORDEM["remoto"]},
            color_discrete_map={"Presencial": "#4DA3FF", "Híbrido": "#FFB547", "Remoto": "#FF6B9A"},
            title="Modelo de trabalho por senioridade",
            labels={"pct": "Participação", "senioridade": "", "remoto": "Modelo"},
        )
        fig.update_traces(offsetgroup="", textangle=0, textposition="inside", insidetextanchor="middle")
        fig.update_layout(yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    tamanho = (df_f.groupby(["tamanho_empresa", "senioridade"])["usd"]
               .agg(mediana="median", registros="size").reset_index())
    fig = px.bar(
        tamanho, x="tamanho_empresa", y="mediana", color="senioridade", barmode="group",
        hover_data={"registros": True},
        category_orders={"tamanho_empresa": ORDEM["tamanho_empresa"], "senioridade": ORDEM["senioridade"]},
        title="Salário mediano por tamanho da empresa e senioridade",
        labels={"mediana": "Mediana anual (USD)", "tamanho_empresa": "Tamanho da empresa",
                "senioridade": "Senioridade"},
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Empresas pequenas têm poucos registros: passe o mouse para ver o tamanho de cada amostra.")

with aba_geo:
    cargos_opcoes = df_f["cargo"].value_counts().index.tolist()
    opcoes_mapa = ["Todos os cargos"] + cargos_opcoes
    indice = opcoes_mapa.index("Data Scientist") if "Data Scientist" in opcoes_mapa else 0
    cargo_mapa = st.selectbox("Cargo", opcoes_mapa, index=indice)
    base_mapa = df_f if cargo_mapa == "Todos os cargos" else df_f[df_f["cargo"] == cargo_mapa]
    paises = (base_mapa.dropna(subset=["residencia_iso3"])
              .groupby(["residencia_iso3", "residencia"])["usd"]
              .agg(mediana="median", registros="size").reset_index())
    g1, g2 = st.columns([3, 2])
    with g1:
        fig = px.choropleth(
            paises, locations="residencia_iso3", color="mediana",
            color_continuous_scale=ESCALA_CONTINUA, hover_name="residencia_iso3",
            hover_data={"registros": True, "residencia_iso3": False},
            title=f"Salário mediano por país: {cargo_mapa}",
            labels={"mediana": "Mediana (USD)"},
        )
        fig.update_geos(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False,
                        showland=True, landcolor="#1A1F3D", projection_type="natural earth")
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)
    with g2:
        top_paises = paises.query("registros >= 10").nlargest(10, "mediana").sort_values("mediana")
        fig = px.bar(
            top_paises, x="mediana", y="residencia_iso3", orientation="h",
            color_discrete_sequence=["#FF6B9A"], text=top_paises["mediana"].map(usd),
            hover_data={"registros": True},
            title="Top 10 países (mín. 10 registros)",
            labels={"mediana": "Mediana anual (USD)", "residencia_iso3": ""},
        )
        fig.update_traces(textposition="outside", cliponaxis=False)
        if not top_paises.empty:
            fig.update_xaxes(range=[0, top_paises["mediana"].max() * 1.3])
        fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

with aba_dados:
    st.markdown(f"**{len(df_f):,} registros** com os filtros atuais.".replace(",", "."))
    st.dataframe(
        df_f, use_container_width=True, hide_index=True,
        column_config={
            "ano": st.column_config.NumberColumn("Ano", format="%d"),
            "usd": st.column_config.NumberColumn("Salário (USD)", format="$%d"),
            "salario": st.column_config.NumberColumn("Salário (moeda original)", format="%d"),
        },
    )
    st.download_button(
        "⬇️ Baixar dados filtrados (CSV)", df_f.to_csv(index=False).encode("utf-8"),
        file_name="salarios_filtrados.csv", mime="text/csv",
    )

with aba_sobre:
    if ARQUIVO_README.exists():
        st.markdown(ARQUIVO_README.read_text(encoding="utf-8"))
