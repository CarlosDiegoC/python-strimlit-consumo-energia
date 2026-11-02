import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.theme import *
from charts.common import layout

def area_chart(data, x, y, color, title, subtitle):
    fig = px.area(data, x=x, y=y, color=color, color_discrete_map=PALETTE,
                  color_discrete_sequence=SEQUENCE, groupnorm=None)
    fig.update_layout(title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0))
    fig.update_traces(line=dict(width=0.5))
    return layout(fig, 450)

def horizontal_bar(data, x, y, title, subtitle="", color=None, height=430, text=None):
    fig = px.bar(data, x=x, y=y, orientation="h", color=color,
                 color_discrete_map=PALETTE, color_discrete_sequence=SEQUENCE,
                 text=text or x)
    fig.update_traces(texttemplate="%{text:,.1f}", textposition="outside",
                      cliponaxis=False, marker_line_width=0)
    fig.update_layout(title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0),
                      yaxis=dict(categoryorder="total ascending"), showlegend=bool(color))
    return layout(fig, height)

def stacked_share(data, title, subtitle):
    long = data.reset_index().melt(id_vars="Ano", var_name="Categoria", value_name="Participação (%)")
    fig = px.area(long, x="Ano", y="Participação (%)", color="Categoria",
                  color_discrete_map=PALETTE, color_discrete_sequence=SEQUENCE)
    fig.update_layout(title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0),
                      yaxis=dict(range=[0,100], ticksuffix="%"))
    return layout(fig, 440)
