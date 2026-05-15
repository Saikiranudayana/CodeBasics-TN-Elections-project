"""components/metrics.py — Reusable KPI card components."""

import streamlit as st


def metric_card(label: str, value, delta=None, delta_label: str = "", help_text: str = ""):
    """Render a styled metric card using HTML."""
    delta_html = ""
    if delta is not None:
        cls = "delta-pos" if delta >= 0 else "delta-neg"
        sign = "+" if delta >= 0 else ""
        delta_html = f'<div class="delta {cls}">{sign}{delta} {delta_label}</div>'
    html = f"""
    <div class="metric-card">
        <h3>{label}</h3>
        <div class="value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    if help_text:
        st.caption(help_text)


def party_badge(party: str, color: str):
    """Render a coloured party badge."""
    st.markdown(
        f'<span class="party-badge" style="background-color:{color}">{party}</span>',
        unsafe_allow_html=True,
    )


def drastic_alert_box(title: str, body: str):
    """Render a pulsing drastic alert box."""
    st.markdown(
        f'<div class="drastic-alert">🚨 {title}<br><span style="font-weight:normal;font-size:14px;">{body}</span></div>',
        unsafe_allow_html=True,
    )


def election_banner(title: str, subtitle: str):
    """Render the top election banner."""
    st.markdown(
        f'<div class="election-banner"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )
