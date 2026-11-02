import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.theme import *
from charts.common import layout

def concentration_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data["Posicao"], y=data["Participacao_acumulada(%)"],
                             mode="lines", line=dict(color=BLUE, width=3),
                             fill="tozeroy", fillcolor="rgba(27,79,114,.07)"))
    marks = data[data["Posicao"].isin([1,5,10,15,20,27])]
    fig.add_trace(go.Scatter(x=marks["Posicao"], y=marks["Participacao_acumulada(%)"],
                             mode="markers+text", text=marks["UF"] + " (" + marks["Participacao_acumulada(%)"].round(1).astype(str) + "%)",
                             textposition="top center", marker=dict(color=BLUE, size=8), showlegend=False))
    fig.update_layout(title="<b>Concentração acumulada do consumo por posição das UFs</b><br><sup>Participação acumulada no consumo nacional (2004–2025)</sup>",
                      yaxis=dict(range=[0,105], ticksuffix="%"))
    return layout(fig, 430)
