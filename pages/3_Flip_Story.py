"""pages/3_Flip_Story.py — Constituency flip analysis."""

import datetime
import traceback
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from components.styles import inject_css, STREAMLIT_CONFIG, top_nav
from components.charts import sankey_flip
from utils.data_loader import load_winners, load_flip_seats
from utils.constants import REGION_ORDER, PARTY_COLORS

st.set_page_config(**STREAMLIT_CONFIG)
inject_css()
top_nav("flip")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

try:
    with st.spinner("Loading flip data…"):
        w21 = load_winners(2021)
        w26 = load_winners(2026)
        flip_df = load_flip_seats()

    total_flips = int(flip_df["is_flip"].sum())
    flipped = flip_df[flip_df["is_flip"]].copy()

    st.title("🔄 Flip Story")
    st.caption("Which constituencies changed hands between 2021 and 2026?")

    # ── SECTION 1: Headline metrics ───────────────────────────────────────────
    pct = total_flips / 234 * 100
    st.markdown(
        f'<div class="election-banner">'
        f'<h1>{total_flips} of 234 constituencies changed hands in 2026</h1>'
        f'<p>That is {pct:.1f}% of all seats — a significant political realignment.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Seats Flipped", total_flips)
    col2.metric("Flip Rate", f"{pct:.1f}%")
    col3.metric("Retained", 234 - total_flips)

    st.markdown("---")

    # ── SECTION 2: Sankey Diagram ─────────────────────────────────────────────
    st.subheader("Where did seats go? 2021 → 2026")
    try:
        fig_sankey = sankey_flip(flip_df)
        st.plotly_chart(fig_sankey, use_container_width=True)
    except Exception as e:
        st.warning(f"Sankey diagram unavailable: {e}")

    st.markdown("---")

    # ── SECTION 3: Flip Heatmap by Region ─────────────────────────────────────
    st.subheader("Flips vs Retained by Region")
    region_flip_data = []
    for region in REGION_ORDER:
        r = flip_df[flip_df["region"] == region]
        flips = int(r["is_flip"].sum())
        retained = len(r) - flips
        region_flip_data.append({"Region": region, "Flipped": flips, "Retained": retained})
    region_flip_df = pd.DataFrame(region_flip_data)

    fig_heat = go.Figure(data=[
        go.Bar(name="Flipped", x=region_flip_df["Region"], y=region_flip_df["Flipped"],
               marker_color="#e94560", text=region_flip_df["Flipped"], textposition="auto"),
        go.Bar(name="Retained", x=region_flip_df["Region"], y=region_flip_df["Retained"],
               marker_color="#4a90d9", text=region_flip_df["Retained"], textposition="auto"),
    ])
    fig_heat.update_layout(barmode="stack", template="plotly_dark", height=380,
                           title="Flipped vs Retained Seats by Region")
    st.plotly_chart(fig_heat, use_container_width=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button("⬇ Download region flip data", region_flip_df.to_csv(index=False),
                       file_name=f"tn_election_region_flip_{ts}.csv", mime="text/csv")

    st.markdown("---")

    # ── SECTION 4: Notable Flips Spotlight ────────────────────────────────────
    st.subheader("🔦 Notable Flips — High Vote Share in 2021 but Still Lost")
    # Merge to get 2021 vote share for flipped seats
    notable = flipped.merge(
        w21[["ac_number", "winner_vote_share", "margin_pct"]].rename(
            columns={"winner_vote_share": "vs21", "margin_pct": "mp21"}),
        on="ac_number", how="left",
    ).merge(
        w26[["ac_number", "winner_vote_share", "margin_pct"]].rename(
            columns={"winner_vote_share": "vs26", "margin_pct": "mp26"}),
        on="ac_number", how="left",
    )
    top5 = notable.nlargest(5, "vs21")

    spotlight_cols = st.columns(2)
    for i, (_, row) in enumerate(top5.iterrows()):
        with spotlight_cols[i % 2]:
            st.markdown(
                f'<div class="spotlight-card">'
                f'<b>{row["constituency"]}</b> ({row.get("region", "")})<br>'
                f'2021: <b>{row["winner_party_2021"]}</b> — margin {row.get("mp21", 0):.1f}%, '
                f'vote share {row.get("vs21", 0):.1f}%<br>'
                f'2026: <b>{row["winner_party_2026"]}</b> — margin {row.get("mp26", 0):.1f}%'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── SECTION 5: Full Flip Table ─────────────────────────────────────────────
    st.subheader("All Flipped Constituencies")
    region_filter = st.multiselect("Filter by region:", REGION_ORDER, default=REGION_ORDER)
    filtered = flipped[flipped["region"].isin(region_filter)][[
        "constituency", "region", "reserved",
        "winner_party_2021", "winner_party_2026",
        "margin_2021", "margin_2026",
    ]].rename(columns={
        "winner_party_2021": "Party 2021",
        "winner_party_2026": "Party 2026",
        "margin_2021": "Margin 2021",
        "margin_2026": "Margin 2026",
    })
    st.dataframe(filtered, use_container_width=True)
    st.download_button("⬇ Download flip data", filtered.to_csv(index=False),
                       file_name=f"tn_election_all_flips_{ts}.csv", mime="text/csv")

except Exception as e:
    st.error(f"Page error: {e}")
    with st.expander("Report Issue"):
        st.code(traceback.format_exc())

st.markdown('<div class="footer">Data source: Election Commission of India | Built for AtliQ Media</div>',
            unsafe_allow_html=True)
