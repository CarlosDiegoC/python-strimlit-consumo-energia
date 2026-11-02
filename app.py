from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px
from services.data_loader import load_energy_file, monthly_industrial_file
from services.data_processing import clean_energy_data
from services.analytics import *
from charts import *
from config.theme import *
from components.filters import render_filters
from components.kpi_cards import kpi

st.set_page_config(page_title="Consumo de Energia Elétrica | Brasil", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: Inter, sans-serif; }}
.stApp {{ background: #F6F8FA; }}
.block-container {{ padding-top: 1.8rem; padding-bottom: 2rem; max-width: 1600px; }}
[data-testid="stSidebar"] {{ background: #F0F3F5; }}
h1,h2,h3 {{ color: {TEXT}; }}
.kpi {{ background: white; border: 1px solid #E7ECEF; border-radius: 10px; padding: 16px 18px; min-height: 112px; }}
.kpi-label {{ color: {MUTED}; font-size: 0.82rem; font-weight: 600; }}
.kpi-value {{ color: {BLUE}; font-size: 1.65rem; font-weight: 800; margin-top: 6px; }}
.kpi-help {{ color: {MUTED}; font-size: 0.75rem; margin-top: 2px; }}
.section-note {{ color: {MUTED}; font-size: .9rem; }}
</style>
""", unsafe_allow_html=True)

st.title("Consumo de Energia Elétrica no Brasil")
st.markdown("<p class='section-note'>Painel analítico | Consumo mensal por UF, região, classe e tipo de consumidor</p>", unsafe_allow_html=True)

DATA_DIR = Path(__file__).resolve().parent / "data"
ENERGY_FILE = DATA_DIR / "Dados_abertos_Consumo_Mensal_Por_UF.xlsx"
INDUSTRIAL_FILE = DATA_DIR / "producao_industrial_limpo.csv"

@st.cache_data(show_spinner="Carregando dados de consumo...")
def get_energy_data(path, modified_at):
    raw = load_energy_file(path)
    df, _ = clean_energy_data(raw)
    return df

@st.cache_data(show_spinner=False)
def get_industrial_data(path, modified_at):
    return monthly_industrial_file(path)

try:
    df = get_energy_data(str(ENERGY_FILE), ENERGY_FILE.stat().st_mtime_ns)
    industrial = get_industrial_data(str(INDUSTRIAL_FILE), INDUSTRIAL_FILE.stat().st_mtime_ns)
except (OSError, ValueError, KeyError) as exc:
    st.error(f"Não foi possível carregar os dados locais: {exc}")
    st.stop()

years, f = render_filters(df)

if f.empty:
    st.warning("Nenhum registro corresponde à combinação de filtros.")
    st.stop()

annual = annual_total(f)
monthly = monthly_total(f)
total_mwh = f["Consumo(MWh)"].sum()
last_year = int(annual["Ano"].max())
last_total = annual.loc[annual["Ano"].eq(last_year), "Consumo(TWh)"].iloc[0]
first_total = annual["Consumo(TWh)"].iloc[0]
growth = (last_total / first_total - 1) * 100 if first_total else 0
consumers = f["Consumidores"].sum() if "Consumidores" in f.columns else None

st.subheader("Visão geral")
cols = st.columns(4)
with cols[0]: kpi("Consumo acumulado", f"{total_mwh/1e6:,.1f} TWh".replace(",", "X").replace(".", ",").replace("X", "."), f"{years[0]}–{years[1]}")
with cols[1]: kpi(f"Consumo em {last_year}", f"{last_total:,.1f} TWh".replace(",", "X").replace(".", ",").replace("X", "."), "Último ano disponível no filtro")
with cols[2]: kpi("Variação no período", f"{growth:+.1f}%".replace(".", ","), "Primeiro versus último ano do filtro")
with cols[3]: kpi("Registros analisados", f"{len(f):,}".replace(",", "."), f"{f['UF'].nunique()} UFs selecionadas")

tabs = st.tabs(["Visão geral", "Perfil de consumo", "Regiões e UFs", "Dados"])

with tabs[0]:
    st.subheader("Evolução do consumo")
    st.plotly_chart(line_chart(annual, "Ano", "Consumo(TWh)",
        title="Consumo anual de energia elétrica no Brasil",
        subtitle="Consumo total anual em Terawatts-hora (TWh)"), use_container_width=True)
    complete_years = f.groupby("Ano")["Data"].nunique()
    full_years = complete_years[complete_years.eq(12)].index
    annual_variation = annual[annual["Ano"].isin(full_years)].copy()
    annual_variation["Variacao(%)"] = annual_variation["Consumo(MWh)"].pct_change() * 100
    st.plotly_chart(variation_chart(annual_variation.dropna(subset=["Variacao(%)"])), use_container_width=True)
    if len(full_years) < f["Ano"].nunique():
        st.caption("A variação anual considera somente anos completos; períodos parciais permanecem nos gráficos de consumo.")
    st.plotly_chart(line_chart(monthly, "Data", "Consumo(TWh)",
        title="Consumo mensal de energia elétrica",
        subtitle="Soma mensal dos registros filtrados"), use_container_width=True)

    aligned = monthly_industry_comparison(f, industrial).reset_index()
    if not aligned.empty:
        # Ambos os indicadores usam índice base 100 no primeiro mês em comum.
        cols_to_index = ["Consumo de Energia (TWh)", "Produção Industrial"]
        aligned = aligned.sort_values("Data")
        for col in cols_to_index:
            base = aligned[col].iloc[0]
            aligned[col] = aligned[col] / base * 100 if base else float("nan")
        fig = px.line(aligned, x="Data", y=cols_to_index, color_discrete_sequence=[BLUE, ORANGE])
        fig.update_layout(title="<b>Energia elétrica e produção industrial</b><br><sup>Índices com base 100 no primeiro mês em comum</sup>")
        st.plotly_chart(layout(fig, 440), use_container_width=True)

with tabs[1]:
    st.subheader("Consumo por classe")
    c1, c2 = st.columns(2)
    classe = by_category(f, "Classe")
    with c1:
        st.plotly_chart(horizontal_bar(classe.sort_values("Participacao(%)"), "Participacao(%)", "Classe",
            "Participação por classe", "Participação no consumo acumulado", height=400), use_container_width=True)
    with c2:
        st.dataframe(classe[["Classe","Consumo(TWh)","Participacao(%)"]].style.format({"Consumo(TWh)":"{:.2f}","Participacao(%)":"{:.2f}%"}), use_container_width=True, hide_index=True)
    annual_class = annual_by_category(f, "Classe") / 1e6
    st.plotly_chart(line_chart(annual_class.reset_index().melt("Ano", var_name="Classe", value_name="Consumo (TWh)"),
        "Ano", "Consumo (TWh)", "Classe", "Setores Industrial e Residencial impulsionam a expansão do consumo",
        "Evolução anual por classe em TWh"), use_container_width=True)
    share_class = share_by_category(f, "Classe")
    st.plotly_chart(stacked_share(share_class, "Estrutura de consumo por classe",
        "Composição percentual da participação no consumo total"), use_container_width=True)

    st.divider()
    st.subheader("Mercado livre e mercado cativo")
    tipo = by_category(f, "TipoConsumidor")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(horizontal_bar(tipo.sort_values("Participacao(%)"), "Participacao(%)", "TipoConsumidor",
            "Participação por tipo de consumidor", height=350), use_container_width=True)
    with c2:
        annual_type = annual_by_category(f, "TipoConsumidor") / 1e6
        st.plotly_chart(line_chart(annual_type.reset_index().melt("Ano", var_name="TipoConsumidor", value_name="Consumo (TWh)"),
            "Ano", "Consumo (TWh)", "TipoConsumidor", "Mercado Livre e Mercado Cativo",
            "Evolução anual do consumo por tipo em TWh"), use_container_width=True)
    share_type_class = (f.groupby(["Classe","TipoConsumidor"])["Consumo(MWh)"].sum().unstack(fill_value=0))
    share_type_class = share_type_class.div(share_type_class.sum(axis=1), axis=0)*100
    st.plotly_chart(horizontal_bar(share_type_class.reset_index().melt("Classe", var_name="TipoConsumidor", value_name="Participação (%)"),
        "Participação (%)", "Classe", "Adesão ao Mercado Livre por classe",
        "Participação de consumidores livres e cativos dentro de cada classe",
        color="TipoConsumidor", height=430, text="Participação (%)"), use_container_width=True)

with tabs[2]:
    st.subheader("Distribuição geográfica")
    c1, c2 = st.columns(2)
    uf = by_category(f, "UF")
    reg = by_category(f, "Regiao")
    with c1:
        st.plotly_chart(horizontal_bar(uf.head(10).sort_values("Consumo(TWh)"), "Consumo(TWh)", "UF",
            "Top 10 UFs por consumo acumulado", "Consumo em TWh"), use_container_width=True)
    with c2:
        st.plotly_chart(horizontal_bar(reg.sort_values("Participacao(%)"), "Participacao(%)", "Regiao",
            "Participação por região", "Participação no consumo total"), use_container_width=True)
    annual_region = annual_by_region(f) / 1e6
    st.plotly_chart(line_chart(annual_region.reset_index().melt("Ano", var_name="Regiao", value_name="Consumo (TWh)"),
        "Ano", "Consumo (TWh)", "Regiao", "Evolução do consumo anual por região",
        "Consumo em Terawatts-hora (TWh)"), use_container_width=True)
    st.plotly_chart(stacked_share(share_by_category(f, "Regiao"), "Composição regional do consumo",
        "Participação percentual de cada região ao longo do tempo"), use_container_width=True)

    comparison = uf_comparison(f)
    st.markdown("#### Crescimento percentual por UF: 2004 versus 2025")
    if not comparison.empty:
        top_growth = comparison.dropna(subset=["Variacao(%)"]).head(10).sort_values("Variacao(%)")
        st.plotly_chart(horizontal_bar(top_growth.reset_index(), "Variacao(%)", "UF",
            "Top 10 UFs com maior crescimento percentual",
            "Comparação restrita às UFs com 12 meses registrados em 2004 e 2025",
            height=430), use_container_width=True)
    else:
        st.info("A comparação 2004–2025 exige ambos os anos no período e 12 meses registrados por UF em cada ano.")

    concentration = uf_concentration(f)
    st.plotly_chart(concentration_chart(concentration), use_container_width=True)
    st.dataframe(concentration[["Posicao","UF","Participacao(%)","Participacao_acumulada(%)"]].head(27),
                 use_container_width=True, hide_index=True)

with tabs[3]:
    st.subheader("Base filtrada")
    st.caption("Os filtros da barra lateral são aplicados à tabela e ao arquivo exportado.")
    st.download_button("Baixar dados filtrados (CSV)", f.to_csv(index=False).encode("utf-8-sig"),
                       "consumo_energia_filtrado.csv", "text/csv")
    st.dataframe(f, use_container_width=True, hide_index=True)
