import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.theme import *
from charts.common import layout

def line_chart(data, x, y, color=None, title="", subtitle="", height=420, labels=None):
    fig = px.line(data, x=x, y=y, color=color, color_discrete_map=PALETTE,
                  color_discrete_sequence=SEQUENCE, labels=labels)
    fig.update_traces(line=dict(width=2.6))
    fig.update_layout(title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0))
    return layout(fig, height)

def variation_chart(data):
    colors = [BLUE if x >= 0 else ORANGE for x in data["Variacao(%)"].fillna(0)]
    fig = go.Figure(go.Bar(x=data["Ano"], y=data["Variacao(%)"], marker_color=colors,
                           text=data["Variacao(%)"], texttemplate="%{text:+.1f}%",
                           textposition="outside", cliponaxis=False))
    fig.add_hline(y=0, line_color=GREY)
    fig.update_layout(title="<b>Consumo reflete ciclos de crise e retomada econômica</b><br><sup>Variação percentual entre anos completos</sup>")
    return layout(fig, 420)
