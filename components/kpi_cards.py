import streamlit as st

def kpi(label, value, help_text=""):
    st.markdown(f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value'>{value}</div><div class='kpi-help'>{help_text}</div></div>", unsafe_allow_html=True)
