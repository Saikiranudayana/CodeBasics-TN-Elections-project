"""pages/4_Vote_Share_Story.py — Vote share analysis."""

import datetime
import traceback
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from components.styles import inject_css, STREAMLIT_CONFIG, top_nav
from components.charts import vote_share_diverging, vote_share_small_multiples
from utils.data_loader import load_winners, load_vote_share
from utils.constants import (MAJOR_PARTIES_2021, MAJOR_PARTIES_2026, PARTY_COLORS, REGION_ORDER)

st.set_page_config(**STREAMLIT_CONFIG)
inject_css()
top_nav("vote")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

try:
    with st.spinner("Loading vote share data…"):
        w21 = load_winners(2021)
        w26 = load_winners(2026)
        vs = load_vote_share()

    vs21_state = vs[(vs["year"] == 2021) & (vs["scope"] == "state")]
    vs26_state = vs[(vs["year"] == 2026) & (vs["scope"] == "state")]

    st.title("📊 Vote Share Story")
    st.caption("How did parties' share of the popular vote change between 2021 and 2026?")

    # ── SECTION 1: State-wide Diverging Bar ───────────────────────────────────
    st.subheader("State-wide Vote Share Shift: 2021 → 2026")
    all_parties = sorted(
        set(MAJOR_PARTIES_2021) | set(MAJOR_PARTIES_2026),
        key=lambda p: float(vs26_state[vs26_state["party"] == p]["vote_share_pct"].sum()),
        reverse=True,
    )
    fig_div = vote_share_diverging(vs21_state, vs26_state, all_parties)
    st.plotly_chart(fig_div, use_container_width=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    vs_compare = vs21_state[["party", "vote_share_pct"]].rename(columns={"vote_share_pct": "share_2021"}).merge(
        vs26_state[["party", "vote_share_pct"]].rename(columns={"vote_share_pct": "share_2026"}),
        on="party", how="outer"
    ).fillna(0)
    vs_compare["change_pp"] = vs_compare["share_2026"] - vs_compare["share_2021"]
    st.download_button("⬇ Download vote share data", vs_compare.to_csv(index=False),
                       file_name=f"tn_election_vote_share_{ts}.csv", mime="text/csv")

    st.markdown("---")

    # ── SECTION 2: TVK Focus Panel ────────────────────────────────────────────
    st.subheader("🟠 TVK Focus — New Force in 2026")
    st.caption("Pattern for viewer to consider. No causal claims are made.")

    tvk_total_votes = int(vs26_state[vs26_state["party"] == "TVK"]["votes"].sum())
    tvk_vs = float(vs26_state[vs26_state["party"] == "TVK"]["vote_share_pct"].sum())
    tvk_seats = int((w26["winner_party"] == "TVK").sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("TVK Total Votes", f"{tvk_total_votes:,}")
    col2.metric("TVK Vote Share", f"{tvk_vs:.2f}%")
    col3.metric("TVK Seats Won", tvk_seats)

    # TVK by region
    tvk_region = vs[(vs["year"] == 2026) & (vs["party"] == "TVK") & (vs["scope"].isin(REGION_ORDER))]
    if not tvk_region.empty:
        fig_tvk_reg = px.bar(
            tvk_region.sort_values("vote_share_pct", ascending=False),
            x="scope", y="vote_share_pct", title="TVK Vote Share by Region (2026)",
            color_discrete_sequence=["#FF6B00"],
        )
        fig_tvk_reg.update_layout(template="plotly_dark", height=350,
                                  xaxis_title="Region", yaxis_title="Vote Share %")
        st.plotly_chart(fig_tvk_reg, use_container_width=True)

    # DMK by region 2021 vs 2026
    st.markdown("**DMK vote share by region: 2021 vs 2026**")
    dmk_vs = vs[(vs["party"] == "DMK") & (vs["scope"].isin(REGION_ORDER))].copy()
    dmk_vs["Year"] = dmk_vs["year"].astype(str)
    if not dmk_vs.empty:
        fig_dmk = px.bar(
            dmk_vs, x="scope", y="vote_share_pct", color="Year", barmode="group",
            color_discrete_map={"2021": "#4a90d9", "2026": "#e94560"},
            title="DMK Vote Share by Region (2021 vs 2026)",
            category_orders={"scope": REGION_ORDER},
        )
        fig_dmk.update_layout(template="plotly_dark", height=350,
                               xaxis_title="Region", yaxis_title="Vote Share %")
        st.plotly_chart(fig_dmk, use_container_width=True)

    st.markdown("---")

    # ── SECTION 3: Faceted Small Multiples ────────────────────────────────────
    st.subheader("Vote Share by Region — All Major Parties")
    fig_sm = vote_share_small_multiples(vs, list(set(MAJOR_PARTIES_2021) | set(MAJOR_PARTIES_2026)))
    st.plotly_chart(fig_sm, use_container_width=True)

    st.markdown("---")

    # ── SECTION 4: NOTA and Minor Party Tracker ───────────────────────────────
    st.subheader("🗳️ NOTA and Minor Party Tracker")
    nota21 = float(vs21_state[vs21_state["party"] == "NOTA"]["vote_share_pct"].sum())
    nota26 = float(vs26_state[vs26_state["party"] == "NOTA"]["vote_share_pct"].sum())
    nota_votes21 = int(vs21_state[vs21_state["party"] == "NOTA"]["votes"].sum())
    nota_votes26 = int(vs26_state[vs26_state["party"] == "NOTA"]["votes"].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("NOTA Vote Share 2021", f"{nota21:.2f}%")
    col2.metric("NOTA Vote Share 2026", f"{nota26:.2f}%", delta=f"{nota26-nota21:+.2f} pp")
    col3.metric("NOTA Votes 2026", f"{nota_votes26:,}")

    # Long-tail minor parties (< 1% state-wide)
    minor21 = vs21_state[vs21_state["vote_share_pct"] < 1.0]["votes"].sum()
    minor26 = vs26_state[vs26_state["vote_share_pct"] < 1.0]["votes"].sum()
    grand21 = vs21_state["votes"].sum()
    grand26 = vs26_state["votes"].sum()
    st.markdown(
        f"**Long-tail minor party votes** (parties with <1% state-wide share): "
        f"2021: {int(minor21):,} ({minor21/grand21*100:.1f}%) | "
        f"2026: {int(minor26):,} ({minor26/grand26*100:.1f}%)"
    )

    # NOTA by region
    nota_region = vs[vs["party"] == "NOTA"][["year", "scope", "vote_share_pct"]].copy()
    nota_region = nota_region[nota_region["scope"].isin(REGION_ORDER)]
    nota_region["Year"] = nota_region["year"].astype(str)
    if not nota_region.empty:
        fig_nota = px.bar(nota_region, x="scope", y="vote_share_pct", color="Year", barmode="group",
                          color_discrete_map={"2021": "#4a90d9", "2026": "#e94560"},
                          title="NOTA Vote Share by Region",
                          category_orders={"scope": REGION_ORDER})
        fig_nota.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_nota, use_container_width=True)

except Exception as e:
    st.error(f"Page error: {e}")
    with st.expander("Report Issue"):
        st.code(traceback.format_exc())

st.markdown('<div class="footer">Data source: Election Commission of India | Built for AtliQ Media</div>',
            unsafe_allow_html=True)
