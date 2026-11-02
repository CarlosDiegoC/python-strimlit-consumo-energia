import streamlit as st
from services.data_loader import filter_period

def render_filters(df):
    min_year, max_year = int(df["Ano"].min()), int(df["Ano"].max())
    with st.sidebar:
        st.header("Filtros")
        years = st.slider("Período de análise", min_year, max_year, (min_year, max_year))
        period = filter_period(df, *years)
        regions = sorted(period["Regiao"].dropna().unique().tolist())
        selected_regions = st.multiselect("Região", regions, default=regions)
        uf_options = sorted(period.loc[period["Regiao"].isin(selected_regions), "UF"].dropna().unique().tolist())
        selected_ufs = st.multiselect("UF", uf_options, default=uf_options)
        classes = sorted(period["Classe"].dropna().unique().tolist())
        selected_classes = st.multiselect("Classe", classes, default=classes)
        types = sorted(period["TipoConsumidor"].dropna().unique().tolist())
        selected_types = st.multiselect("Tipo de consumidor", types, default=types)
        systems = sorted(period["Sistema"].dropna().unique().tolist())
        selected_systems = st.multiselect("Sistema", systems, default=systems)
    filtered = period[
        period["Regiao"].isin(selected_regions) & period["UF"].isin(selected_ufs) &
        period["Classe"].isin(selected_classes) & period["TipoConsumidor"].isin(selected_types) &
        period["Sistema"].isin(selected_systems)
    ].copy()
    return years, filtered
