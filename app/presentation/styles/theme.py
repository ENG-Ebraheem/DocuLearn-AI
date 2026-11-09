"""Minimal Arabic-first direction styles for native Streamlit components."""

from __future__ import annotations

import streamlit as st

RTL_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', system-ui, -apple-system, sans-serif;
    direction: rtl;
    text-align: right;
}

section[data-testid="stSidebar"] {
    direction: rtl;
    text-align: right;
}

div[data-testid="stChatMessage"], div[data-testid="stChatInput"] {
    direction: rtl;
    text-align: right;
}

div[data-testid="stChatInput"] textarea {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif;
}

div[data-testid="stMetric"] {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 12px 16px;
}

button[data-testid="baseButton-secondary"], button[data-testid="baseButton-primary"] {
    border-radius: 8px;
    font-family: 'Cairo', sans-serif;
    font-weight: 600;
}
</style>
"""


def apply_theme() -> None:
    """Apply native RTL styling and modern Arabic visual design tokens."""
    st.markdown(RTL_STYLE, unsafe_allow_html=True)

