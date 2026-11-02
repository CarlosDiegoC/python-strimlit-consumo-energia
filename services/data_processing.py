import pandas as pd
import numpy as np

def clean_energy_data(raw: pd.DataFrame):
    """Aplica as regras documentadas no notebook e mantém trilha de auditoria."""
    df = raw.copy()
    df["Ano"] = df["Data"].dt.year
    duplicated = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # Correção específica documentada: RO / Norte / Sistemas Isolados /
    # Comercial / Cativo / 2024, usando mediana dos valores válidos do grupo.
    specific = (
        df["UF"].eq("RO") & df["Regiao"].eq("Norte") &
        df["Sistema"].str.upper().eq("SISTEMAS ISOLADOS") &
        df["Classe"].eq("Comercial") & df["TipoConsumidor"].eq("Cativo") &
        df["Ano"].eq(2024)
    )
    specific_cons = specific & df["Consumidores"].lt(0) if "Consumidores" in df else pd.Series(False, index=df.index)
    if specific_cons.any():
        valid = df.loc[specific & df["Consumidores"].ge(0), "Consumidores"]
        if not valid.empty:
            df.loc[specific_cons, "Consumidores"] = valid.median()

    specific_energy = specific & df["Consumo(MWh)"].lt(0)
    if specific_energy.any():
        valid = df.loc[specific & df["Consumo(MWh)"].ge(0), "Consumo(MWh)"]
        if not valid.empty:
            df.loc[specific_energy, "Consumo(MWh)"] = valid.median()

    # Demais consumos negativos: mediana por UF, região, sistema, classe,
    # tipo de consumidor e ano, conforme a lógica do notebook.
    negative = df["Consumo(MWh)"].lt(0)
    negative_count = int(negative.sum())
    if negative.any():
        keys = ["UF", "Regiao", "Sistema", "Classe", "TipoConsumidor", "Ano"]
        medians = df.loc[~negative].groupby(keys)["Consumo(MWh)"].median()
        for idx in df.index[negative]:
            key = tuple(df.loc[idx, keys])
            replacement = medians.get(key, np.nan)
            if pd.notna(replacement):
                df.loc[idx, "Consumo(MWh)"] = replacement

    # O notebook corrige Consumidores apenas no caso específico acima.
    audit = {
        "duplicadas_removidas": duplicated,
        "consumos_negativos_identificados": negative_count,
        "consumos_negativos_restantes": int(df["Consumo(MWh)"].lt(0).sum()),
        "linhas_apos_tratamento": len(df),
        "linhas_originais": len(raw),
    }
    return df, audit

