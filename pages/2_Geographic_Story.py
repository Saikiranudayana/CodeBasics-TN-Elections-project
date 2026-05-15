"""pages/2_Geographic_Story.py — Regional election analysis."""

import datetime
import traceback
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.styles import inject_css, STREAMLIT_CONFIG, top_nav, render_footer
from components.charts import region_seat_heatmap
from utils.data_loader import load_winners, load_flip_seats
from utils.constants import REGION_ORDER, MAJOR_PARTIES_2021, MAJOR_PARTIES_2026, PARTY_COLORS, RESERVED_ORDER

st.set_page_config(**STREAMLIT_CONFIG)
inject_css()
top_nav("geo")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

try:
    with st.spinner("Loading geographic data…"):
        w21 = load_winners(2021)
        w26 = load_winners(2026)
        flip_df = load_flip_seats()

    st.title("🗺️ Geographic Story")
    st.caption("How did different regions of Tamil Nadu vote in 2021 vs 2026?")

    # ── SECTION 1: Region Seat Heatmap ────────────────────────────────────────
    st.subheader("Region Seat Distribution")
    year_choice = st.radio("Select year:", ["2021", "2026", "Side-by-side"], horizontal=True)

    if year_choice == "2021":
        fig = region_seat_heatmap(w21, MAJOR_PARTIES_2021)
        st.plotly_chart(fig, use_container_width=True)
    elif year_choice == "2026":
        fig = region_seat_heatmap(w26, MAJOR_PARTIES_2026)
        st.plotly_chart(fig, use_container_width=True)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.caption("2021")
            st.plotly_chart(region_seat_heatmap(w21, MAJOR_PARTIES_2021), use_container_width=True)
        with col2:
            st.caption("2026")
            st.plotly_chart(region_seat_heatmap(w26, MAJOR_PARTIES_2026), use_container_width=True)

    st.markdown("---")

    # ── SECTION 2: Region-level Swing Table ───────────────────────────────────
    st.subheader("Region-level Swing Summary")

    rows = []
    key_parties = ["DMK", "AIADMK", "TVK"]
    for region in REGION_ORDER:
        r21 = w21[w21["region"] == region]
        r26 = w26[w26["region"] == region]
        total_seats = len(r26)
        dom21 = r21["winner_party"].value_counts().idxmax() if not r21.empty else "—"
        dom26 = r26["winner_party"].value_counts().idxmax() if not r26.empty else "—"
        row = {
            "Region": region,
            "Total Seats": total_seats,
            "Dominant 2021": dom21,
            "Dominant 2026": dom26,
        }
        for party in key_parties:
            s21 = int((r21["winner_party"] == party).sum())
            s26 = int((r26["winner_party"] == party).sum())
            row[f"{party} 2021"] = s21
            row[f"{party} 2026"] = s26
            row[f"{party} Δ"] = s26 - s21
        rows.append(row)

    swing_df = pd.DataFrame(rows)

    def color_delta(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return "color: #4caf50; font-weight: bold;"
            elif val < 0:
                return "color: #f44336; font-weight: bold;"
        return ""

    delta_cols = [c for c in swing_df.columns if "Δ" in c]
    styled = swing_df.style.map(color_delta, subset=delta_cols)
    st.dataframe(styled, use_container_width=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button("⬇ Download region swing data", swing_df.to_csv(index=False),
                       file_name=f"tn_election_region_swing_{ts}.csv", mime="text/csv")

    st.markdown("---")

    # ── SECTION 3: Region Selector Drill-down ─────────────────────────────────
    st.subheader("Constituency Drill-down")
    selected_region = st.selectbox("Select a region:", REGION_ORDER)

    r21_sel = w21[w21["region"] == selected_region][
        ["ac_number", "constituency", "winner_party", "winner_votes", "winner_vote_share", "margin_pct"]
    ].rename(columns={
        "winner_party": "party_2021", "winner_votes": "votes_2021",
        "winner_vote_share": "share_2021", "margin_pct": "margin_pct_2021",
    })
    r26_sel = w26[w26["region"] == selected_region][
        ["ac_number", "constituency", "winner_party", "winner_votes", "winner_vote_share", "margin_pct"]
    ].rename(columns={
        "winner_party": "party_2026", "winner_votes": "votes_2026",
        "winner_vote_share": "share_2026", "margin_pct": "margin_pct_2026",
    })

    merged = r26_sel.merge(r21_sel[["ac_number", "party_2021", "votes_2021", "share_2021", "margin_pct_2021"]],
                           on="ac_number", how="left")
    merged["Flipped"] = merged["party_2021"] != merged["party_2026"]
    merged["Margin Δ"] = (merged["margin_pct_2026"] - merged["margin_pct_2021"]).round(2)

    display_cols = ["constituency", "party_2021", "votes_2021", "share_2021",
                    "party_2026", "votes_2026", "share_2026", "Flipped", "Margin Δ"]

    def highlight_flips(row):
        if row.get("Flipped", False):
            return ["background-color: rgba(233,69,96,0.15)"] * len(row)
        return [""] * len(row)

    styled_drill = merged[display_cols].style.apply(highlight_flips, axis=1)
    st.dataframe(styled_drill, use_container_width=True)

    st.markdown("---")

    # ── SECTION 4: Reserved Seat Breakdown ────────────────────────────────────
    st.subheader("Reserved Seat Breakdown")
    col_sc, col_gen = st.columns(2)

    for col, cat, label in [(col_gen, "GEN", "GEN Seats"), (col_sc, "SC", "SC Seats")]:
        with col:
            st.markdown(f"**{label}**")
            for year, w in [(2021, w21), (2026, w26)]:
                sub = w[w["reserved"] == cat]
                party_counts = sub["winner_party"].value_counts().reset_index()
                party_counts.columns = ["party", "seats"]
                party_counts = party_counts[party_counts["seats"] >= 1]
                fig = px.bar(party_counts, x="party", y="seats", title=str(year),
                             color="party", color_discrete_map=PARTY_COLORS, height=250)
                fig.update_layout(template="plotly_dark", showlegend=False, margin=dict(t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Page error: {e}")
    with st.expander("Report Issue"):
        st.code(traceback.format_exc())

render_footer()
