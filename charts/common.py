import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.theme import *

def layout(fig, height=420):
    # Reserve dedicated space for the title above and the legend below.
    # This prevents the legend from overlapping titles or axis labels.
    has_legend = any(trace.showlegend is not False and trace.name for trace in fig.data)
    fig.update_layout(
        height=height + (65 if has_legend else 15),
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Arial", color=TEXT),
        margin=dict(l=55, r=35, t=105, b=100 if has_legend else 45),
        title=dict(y=0.97, yanchor="top", x=0, xanchor="left"),
        legend=dict(orientation="h", x=0, xanchor="left", y=-0.24,
                    yanchor="top", title_text=""),
        hoverlabel=dict(bgcolor="white", font_color=TEXT)
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title=None)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, title=None)
    return fig
