import pandas as pd
import numpy as np

def annual_total(df):
    out = df.groupby("Ano")["Consumo(MWh)"].sum().rename("Consumo(MWh)").reset_index()
    out["Consumo(TWh)"] = out["Consumo(MWh)"] / 1e6
    out["Variacao(%)"] = out["Consumo(MWh)"].pct_change() * 100
    return out

def monthly_total(df):
    return (df.groupby("Data")["Consumo(MWh)"].sum()
            .rename("Consumo(MWh)").reset_index().sort_values("Data")
            .assign(**{"Consumo(TWh)": lambda x: x["Consumo(MWh)"]/1e6}))

def by_category(df, category):
    out = (df.groupby(category)["Consumo(MWh)"].sum()
           .sort_values(ascending=False).rename("Consumo(MWh)").reset_index())
    total = out["Consumo(MWh)"].sum()
    out["Participacao(%)"] = out["Consumo(MWh)"] / total * 100 if total else 0
    out["Consumo(TWh)"] = out["Consumo(MWh)"] / 1e6
    return out

def annual_by_category(df, category):
    return (df.groupby(["Ano", category])["Consumo(MWh)"].sum()
            .unstack(category).sort_index())

def share_by_category(df, category):
    table = annual_by_category(df, category)
    return table.div(table.sum(axis=1), axis=0) * 100

def uf_comparison(df):
    months = df.groupby(["UF", "Ano"])["Data"].nunique().unstack("Ano")
    annual = df.groupby(["UF", "Ano"])["Consumo(MWh)"].sum().unstack("Ano")
    if 2004 not in months or 2025 not in months or 2004 not in annual or 2025 not in annual:
        return pd.DataFrame()
    comparable = months.index[(months[2004] == 12) & (months[2025] == 12)]
    result = annual.loc[annual.index.intersection(comparable), [2004, 2025]].copy()
    result.columns = ["Consumo_2004", "Consumo_2025"]
    result["Variacao_MWh"] = result["Consumo_2025"] - result["Consumo_2004"]
    result["Variacao(%)"] = result["Variacao_MWh"] / result["Consumo_2004"].replace(0, np.nan) * 100
    return result.sort_values("Variacao(%)", ascending=False)

def uf_concentration(df):
    out = by_category(df, "UF")
    out["Posicao"] = range(1, len(out)+1)
    out["Participacao_acumulada(%)"] = out["Participacao(%)"].cumsum()
    return out

def annual_by_region(df):
    return annual_by_category(df, "Regiao")

def monthly_industry_comparison(df, industrial):
    energy = monthly_total(df).set_index("Data")["Consumo(TWh)"]
    aligned = pd.concat([energy.rename("Consumo de Energia (TWh)"),
                         industrial["Indústria geral"].rename("Produção Industrial")], axis=1)
    return aligned.dropna()
