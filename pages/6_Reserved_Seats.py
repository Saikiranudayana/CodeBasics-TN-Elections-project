"""pages/6_Reserved_Seats.py — Reserved constituency analysis."""

import datetime
import traceback
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.styles import inject_css, STREAMLIT_CONFIG, top_nav, render_footer
from utils.data_loader import load_winners, load_flip_seats
from utils.constants import PARTY_COLORS, REGION_ORDER, RESERVED_ORDER

st.set_page_config(**STREAMLIT_CONFIG)
inject_css()
top_nav("reserved")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

try:
    with st.spinner("Loading reserved seat data…"):
        w21 = load_winners(2021)
        w26 = load_winners(2026)
        flip_df = load_flip_seats()

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    st.title("⚖️ Reserved Seats Analysis")
    st.caption("GEN, SC, and ST constituency breakdown — 2021 vs 2026.")

    # ── SECTION 1: Summary Comparison ────────────────────────────────────────
    st.subheader("Category Summary: GEN | SC | ST")
    cols = st.columns(3)
    for col, cat in zip(cols, RESERVED_ORDER):
        with col:
            r21 = w21[w21["reserved"] == cat]
            r26 = w26[w26["reserved"] == cat]
            total = len(r26)
            st.markdown(f"### {cat} Seats ({total})")

            for year, w, color in [(2021, r21, "#4a90d9"), (2026, r26, "#e94560")]:
                pc = w["winner_party"].value_counts().reset_index()
                pc.columns = ["party", "seats"]
                pc = pc[pc["seats"] >= 1]
                fig = go.Figure(go.Pie(
                    labels=pc["party"], values=pc["seats"], hole=0.5,
                    marker_colors=[PARTY_COLORS.get(p, "#CCCCCC") for p in pc["party"]],
                ))
                fig.update_layout(
                    title=str(year), template="plotly_dark", height=250,
                    showlegend=True, margin=dict(t=30, b=10, l=10, r=10),
                    annotations=[dict(text=str(year), x=0.5, y=0.5, font_size=16, showarrow=False, font_color="white")],
                )
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── SECTION 2: Did Reserved Seats Behave Differently? ────────────────────
    st.subheader("Did Reserved Seats Behave Differently?")

    rows = []
    for cat in RESERVED_ORDER:
        f_cat = flip_df[flip_df["reserved"] == cat]
        w21_cat = w21[w21["reserved"] == cat]
        w26_cat = w26[w26["reserved"] == cat]

        flip_rate = f_cat["is_flip"].mean() * 100 if len(f_cat) > 0 else 0
        avg_margin21 = w21_cat["margin_pct"].mean() if not w21_cat.empty else 0
        avg_margin26 = w26_cat["margin_pct"].mean() if not w26_cat.empty else 0

        rows.append({
            "Category": cat,
            "Total Seats": len(w26_cat),
            "Flip Rate %": round(flip_rate, 1),
            "Avg Margin % 2021": round(avg_margin21, 2),
            "Avg Margin % 2026": round(avg_margin26, 2),
            "Margin Δ": round(avg_margin26 - avg_margin21, 2),
        })

    comp_df = pd.DataFrame(rows)

    def color_margin_delta(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return "color: #4caf50; font-weight: bold;"
            elif val < 0:
                return "color: #f44336; font-weight: bold;"
        return ""

    styled = comp_df.style.map(color_margin_delta, subset=["Margin Δ"])
    st.dataframe(styled, use_container_width=True)

    # Party vote share by reserved category
    st.markdown("**Party seat distribution by reserved category (2026):**")
    party_reserved = w26.groupby(["reserved", "winner_party"]).size().reset_index(name="seats")
    fig_pr = px.bar(
        party_reserved, x="winner_party", y="seats", color="reserved",
        barmode="group", title="Party Seats by Reserved Category (2026)",
        color_discrete_map={"GEN": "#4a90d9", "SC": "#e94560", "ST": "#f39c12"},
    )
    fig_pr.update_layout(template="plotly_dark", height=380,
                         xaxis_title="Party", yaxis_title="Seats")
    st.plotly_chart(fig_pr, use_container_width=True)

    st.markdown("---")

    # ── SECTION 3: SC Seat Deep-dive ──────────────────────────────────────────
    st.subheader("SC Constituency Deep-dive (44 seats)")
    region_filter = st.selectbox("Filter SC seats by region:", ["All"] + REGION_ORDER)

    sc21 = w21[w21["reserved"] == "SC"][["ac_number", "constituency", "region", "winner_party", "margin_pct"]].rename(
        columns={"winner_party": "party_2021", "margin_pct": "margin_2021"})
    sc26 = w26[w26["reserved"] == "SC"][["ac_number", "constituency", "region", "winner_party", "margin_pct"]].rename(
        columns={"winner_party": "party_2026", "margin_pct": "margin_2026"})

    sc_merged = sc26.merge(sc21[["ac_number", "party_2021", "margin_2021"]], on="ac_number", how="left")
    sc_merged["Flipped"] = sc_merged["party_2021"] != sc_merged["party_2026"]

    if region_filter != "All":
        sc_merged = sc_merged[sc_merged["region"] == region_filter]

    display = sc_merged[["constituency", "region", "party_2021", "party_2026", "Flipped", "margin_2021", "margin_2026"]]
    display.columns = ["Constituency", "Region", "Party 2021", "Party 2026", "Flipped", "Margin % 2021", "Margin % 2026"]

    def highlight_sc_flips(row):
        if row.get("Flipped", False):
            return ["background-color: rgba(233,69,96,0.15)"] * len(row)
        return [""] * len(row)

    styled_sc = display.style.apply(highlight_sc_flips, axis=1)
    st.dataframe(styled_sc, use_container_width=True)
    st.download_button("⬇ Download SC data", display.to_csv(index=False),
                       file_name=f"tn_election_SC_seats_{ts}.csv", mime="text/csv")

except Exception as e:
    st.error(f"Page error: {e}")
    with st.expander("Report Issue"):
        st.code(traceback.format_exc())

render_footer()
