from __future__ import annotations
import pandas as pd
import numpy as np

REQUIRED = {"UF", "Regiao", "Sistema", "Classe", "TipoConsumidor", "Consumo(MWh)"}

def load_energy_file(uploaded_file) -> pd.DataFrame:
    name = str(getattr(uploaded_file, "name", uploaded_file)).lower()
    if name.endswith((".xlsx", ".xls")):
        raw = pd.read_excel(uploaded_file)
    elif name.endswith(".csv"):
        try:
            raw = pd.read_csv(uploaded_file, sep=None, engine="python", encoding="utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            raw = pd.read_csv(uploaded_file, sep=None, engine="python", encoding="latin-1")
    else:
        raise ValueError("Formato não suportado. Envie um arquivo XLSX, XLS ou CSV.")

    # Reproduz a padronização feita no notebook.
    if "DataExcel" in raw.columns:
        # No notebook, a coluna Data original é descartada e DataExcel passa
        # a ser a coluna temporal usada nas análises.
        raw = raw.drop(columns=["Data"], errors="ignore")
        raw = raw.rename(columns={"DataExcel": "Data"})
    if "Consumo" in raw.columns:
        raw = raw.rename(columns={"Consumo": "Consumo(MWh)"})
    raw = raw.drop(columns=[c for c in ["DataVersao", "DataExcel"] if c in raw.columns], errors="ignore")

    if "Data" not in raw.columns:
        raise ValueError("Coluna de data não encontrada. Esperado: DataExcel ou Data.")
    if "Data" in raw.columns and pd.api.types.is_numeric_dtype(raw["Data"]):
        # DataExcel é serial do Excel; origin compatível com o sistema Excel.
        raw["Data"] = pd.to_datetime(raw["Data"], unit="D", origin="1899-12-30", errors="coerce")
    else:
        raw["Data"] = pd.to_datetime(raw["Data"], errors="coerce", dayfirst=True)

    missing = REQUIRED - set(raw.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(sorted(missing))}")

    raw["Consumo(MWh)"] = pd.to_numeric(raw["Consumo(MWh)"], errors="coerce")
    if "Consumidores" in raw.columns:
        raw["Consumidores"] = pd.to_numeric(raw["Consumidores"], errors="coerce")

    raw = raw.dropna(subset=["Data", "Consumo(MWh)"]).copy()
    for col in ["UF", "Regiao", "Sistema", "Classe", "TipoConsumidor"]:
        raw[col] = raw[col].astype(str).str.strip()
    return raw


def filter_period(df, start_year, end_year):
    return df.loc[df["Ano"].between(start_year, end_year)].copy()


def monthly_industrial_file(path):
    ind = pd.read_csv(path, index_col="Data", parse_dates=["Data"])
    if "Indústria geral" not in ind.columns:
        raise ValueError("Coluna 'Indústria geral' ausente na base industrial.")
    ind["Indústria geral"] = pd.to_numeric(ind["Indústria geral"], errors="coerce")
    return ind.sort_index()
