"""pages/5_Margin_Story.py — Margin of victory analysis."""

import datetime
import traceback
import streamlit as st
import pandas as pd

from components.styles import inject_css, STREAMLIT_CONFIG, top_nav, render_footer
from components.charts import margin_histogram, margin_scatter
from utils.data_loader import load_winners, load_margin_analysis

st.set_page_config(**STREAMLIT_CONFIG)
inject_css()
top_nav("margin")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

try:
    with st.spinner("Loading margin data…"):
        w21 = load_winners(2021)
        w26 = load_winners(2026)
        margin_df = load_margin_analysis()

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    st.title("📏 Margin of Victory Story")
    st.caption("How decisive were the victories in 2026 compared to 2021?")

    # ── SECTION 1: Distribution Histogram ─────────────────────────────────────
    st.subheader("Distribution of Winning Margins")
    fig_hist = margin_histogram(w21, w26)
    st.plotly_chart(fig_hist, use_container_width=True)
    hist_data = pd.DataFrame({
        "margin_pct_2021": w21["margin_pct"].values,
        "constituency_2021": w21["constituency"].values,
    }).merge(
        pd.DataFrame({"margin_pct_2026": w26["margin_pct"].values, "constituency_2026": w26["constituency"].values}),
        left_index=True, right_index=True, how="outer"
    )
    st.download_button("⬇ Download margin distribution data", w21[["constituency", "margin_pct"]].to_csv(index=False),
                       file_name=f"tn_election_margin_dist_2021_{ts}.csv", mime="text/csv")

    st.markdown("---")

    # ── SECTION 2: Landslide vs Narrow Win Table ──────────────────────────────
    st.subheader("Win Category Breakdown")

    def categorise(vs):
        if vs >= 50:
            return "Landslide"
        elif vs >= 40:
            return "Comfortable"
        else:
            return "Narrow"

    w21c = w21.copy(); w21c["category"] = w21c["winner_vote_share"].apply(categorise)
    w26c = w26.copy(); w26c["category"] = w26c["winner_vote_share"].apply(categorise)

    cats = ["Landslide", "Comfortable", "Narrow"]
    cat_rows = []
    for cat in cats:
        n21 = int((w21c["category"] == cat).sum())
        n26 = int((w26c["category"] == cat).sum())
        cat_rows.append({
            "Category": cat,
            "Criteria": {"Landslide": "≥50% vote share", "Comfortable": "40–50%", "Narrow": "<40%"}[cat],
            "2021 Count": n21,
            "2021 %": f"{n21/234*100:.1f}%",
            "2026 Count": n26,
            "2026 %": f"{n26/234*100:.1f}%",
            "Change": n26 - n21,
        })
    cat_df = pd.DataFrame(cat_rows)
    st.dataframe(cat_df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    for i, cat in enumerate(cats):
        row = cat_df[cat_df["Category"] == cat].iloc[0]
        [col1, col2, col3][i].metric(
            f"{cat} Wins 2026", row["2026 Count"], delta=int(row["Change"])
        )

    st.markdown("---")

    # ── SECTION 3: Margin Change Scatter ──────────────────────────────────────
    st.subheader("Margin Change: 2021 vs 2026 (per constituency)")
    fig_scatter = margin_scatter(margin_df)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.download_button("⬇ Download margin comparison data", margin_df[
        ["constituency", "region", "winner_party_2021", "winner_party_2026",
         "margin_pct_2021", "margin_pct_2026", "margin_pct_change"]
    ].to_csv(index=False),
                       file_name=f"tn_election_margin_comparison_{ts}.csv", mime="text/csv")

    st.markdown("---")

    # ── SECTION 4: Most Contested Constituencies 2026 ─────────────────────────
    st.subheader("🏁 Most Contested Constituencies in 2026 (Smallest Margin)")
    top20 = w26.nsmallest(20, "margin").copy()
    # Get runner-up party
    runner_up = []
    for _, row in top20.iterrows():
        # Runner-up from margin_analysis
        ma_row = margin_df[margin_df["ac_number"] == row["ac_number"]]
        runner_up.append("—")

    top20_display = top20[["constituency", "region", "winner_party", "margin", "margin_pct"]].copy()
    top20_display.columns = ["Constituency", "Region", "Winner Party", "Margin (Votes)", "Margin %"]
    top20_display["Margin %"] = top20_display["Margin %"].round(2)
    st.dataframe(top20_display, use_container_width=True)
    st.download_button("⬇ Download top 20 closest wins", top20_display.to_csv(index=False),
                       file_name=f"tn_election_closest_wins_2026_{ts}.csv", mime="text/csv")

except Exception as e:
    st.error(f"Page error: {e}")
    with st.expander("Report Issue"):
        st.code(traceback.format_exc())

render_footer()
