"""pages/1_Overview.py — Full constituency results table (reference-style)."""

import datetime
import traceback
import streamlit as st
import pandas as pd

from components.styles import inject_css, STREAMLIT_CONFIG, top_nav, render_footer
from components.charts import party_seat_bar_chart, alliance_donut
from components.drastic_detector import detect_all_drastic_changes
from components.metrics import election_banner, metric_card
from utils.data_loader import load_winners, load_vote_share, load_flip_seats
from utils.constants import ALLIANCE_2021, ALLIANCE_2026, PARTY_COLORS

st.set_page_config(**STREAMLIT_CONFIG)
inject_css()
top_nav("results")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

try:
    with st.spinner("Loading…"):
        w21 = load_winners(2021)
        w26 = load_winners(2026)
        vs  = load_vote_share()
        flip_df = load_flip_seats()

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown("## Full Constituency Results")
    st.caption("Explore detailed winning margins and candidate performance for all 234 assembly constituencies.")

    # ── Two big navigation buttons (reference style) ───────────────────────
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#f97316,#fb923c);border-radius:10px;
             padding:24px 28px;text-align:center;cursor:pointer;">
          <p style="font-size:20px;font-weight:800;color:#fff;margin:0;">District Wise</p>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/2_Geographic_Story.py", label="→ View District-wise analysis", use_container_width=True)
    with c2:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#a855f7,#ec4899);border-radius:10px;
             padding:24px 28px;text-align:center;cursor:pointer;">
          <p style="font-size:20px;font-weight:800;color:#fff;margin:0;">Vote Share</p>
        </div>""", unsafe_allow_html=True)
        st.page_link("pages/4_Vote_Share_Story.py", label="→ View Vote Share analysis", use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Alliance + party map for lookup ──────────────────────────────────
    party_to_alliance = {}
    for alliance, parties in ALLIANCE_2026.items():
        for p in parties:
            party_to_alliance[p] = alliance

    # ── Filter bar ───────────────────────────────────────────────────────
    fcol1, fcol2, fcol3, fcol4 = st.columns([2, 1.5, 1.5, 3])
    districts = sorted(w26["region"].dropna().unique())
    parties_list = sorted(w26["winner_party"].dropna().unique())
    alliance_list = sorted(party_to_alliance.values())
    alliance_list = ["All Alliances"] + sorted(set(alliance_list))

    with fcol1:
        dist_filter = st.selectbox("District / Region", ["All Districts"] + districts, label_visibility="collapsed")
    with fcol2:
        party_filter = st.selectbox("Party", ["All Parties"] + parties_list, label_visibility="collapsed")
    with fcol3:
        alliance_filter = st.selectbox("Alliance", alliance_list, label_visibility="collapsed")
    with fcol4:
        search = st.text_input("Search constituency…", placeholder="Type a name or AC no.", label_visibility="collapsed")

    # ── Party seat pills ─────────────────────────────────────────────────
    party_counts = w26.groupby("winner_party").size().sort_values(ascending=False)
    pills_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 16px;">'
    for party, cnt in party_counts.items():
        color = PARTY_COLORS.get(party, "#555")
        pills_html += (
            f'<span class="party-pill">'
            f'<span class="pill-dot" style="background:{color};"></span>'
            f'{party} <span class="pill-count">{cnt}</span></span>'
        )
    pills_html += "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)

    # ── Build filtered table ──────────────────────────────────────────────
    df = w26.merge(
        flip_df[["ac_number", "winner_party_2021", "is_flip"]],
        on="ac_number", how="left"
    )
    df["alliance"] = df["winner_party"].map(party_to_alliance).fillna("Others")

    if dist_filter != "All Districts":
        df = df[df["region"] == dist_filter]
    if party_filter != "All Parties":
        df = df[df["winner_party"] == party_filter]
    if alliance_filter != "All Alliances":
        df = df[df["alliance"] == alliance_filter]
    if search:
        mask = (
            df["constituency"].str.contains(search, case=False, na=False) |
            df["ac_number"].astype(str).str.contains(search, na=False) |
            df["winner_candidate"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    df = df.sort_values("ac_number").reset_index(drop=True)

    # ── Render HTML table ────────────────────────────────────────────────
    rows_html = ""
    for i, row in df.iterrows():
        color = PARTY_COLORS.get(row["winner_party"], "#555")
        flip_marker = "🔄 " if row.get("is_flip") else ""
        rows_html += f"""
        <tr>
          <td style="color:#555;font-size:12px;">{i+1}</td>
          <td>
            <div class="const-name">{flip_marker}{row['constituency']}</div>
            <div class="const-dist">{row.get('region','')}</div>
          </td>
          <td style="font-weight:500;">{row.get('winner_candidate','—')}</td>
          <td>
            <span class="party-badge" style="background:{color};">{row['winner_party']}</span>
          </td>
          <td style="font-weight:600;">{int(row['margin']):,}</td>
          <td>
            <span style="font-size:11px;color:#666;background:#1a1a1a;padding:2px 8px;border-radius:4px;">
              {row['alliance']}
            </span>
          </td>
        </tr>"""

    table_html = f"""
    <table class="results-table">
      <thead>
        <tr>
          <th>No.</th>
          <th>Constituency</th>
          <th>Elected Candidate</th>
          <th>Party</th>
          <th>Margin ▾</th>
          <th>Alliance</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>"""
    st.markdown(table_html, unsafe_allow_html=True)

    st.caption(f"Showing {len(df)} of 234 constituencies. 🔄 = flipped from 2021.")

    # ── Download ──────────────────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    download_df = df[["ac_number","constituency","region","reserved","winner_candidate","winner_party","alliance","winner_votes","margin","margin_pct","winner_vote_share","is_flip"]].copy()
    st.download_button("⬇ Download full results CSV", download_df.to_csv(index=False),
                       file_name="tn_2026_results_full.csv", mime="text/csv")

    st.markdown("---")

    # ── Seat count chart (kept for analysis) ────────────────────────────
    with st.expander("📊 Party Seat Count Chart (2021 vs 2026)"):
        st.plotly_chart(party_seat_bar_chart(w21, w26, min_seats=2), use_container_width=True)

    with st.expander("🍩 Alliance Donut Charts"):
        ca1, ca2 = st.columns(2)
        with ca1:
            st.plotly_chart(alliance_donut(w21, ALLIANCE_2021, 2021), use_container_width=True)
        with ca2:
            st.plotly_chart(alliance_donut(w26, ALLIANCE_2026, 2026), use_container_width=True)

except Exception as e:
    st.error(f"Page error: {e}")
    with st.expander("Report Issue"):
        st.code(traceback.format_exc())

render_footer()


try:
    with st.spinner("Loading election data…"):
        w21 = load_winners(2021)
        w26 = load_winners(2026)
        vs = load_vote_share()
        flip_df = load_flip_seats()

    # ── SECTION 1: Election Banner ────────────────────────────────────────────
    election_banner(
        "2026 Tamil Nadu Assembly Election Results",
        "234 Seats | Majority mark: 118 | Record turnout: 85.1%",
    )

    # ── SECTION 2: Top KPI Row ────────────────────────────────────────────────
    def alliance_seats(w, alliance_map):
        party_seats = w.groupby("winner_party").size().to_dict()
        return {a: sum(party_seats.get(p, 0) for p in ps) for a, ps in alliance_map.items()}

    a21 = alliance_seats(w21, ALLIANCE_2021)
    a26 = alliance_seats(w26, ALLIANCE_2026)
    dmk21 = a21.get("DMK Alliance", 0)
    dmk26 = a26.get("DMK Alliance", 0)
    aiadmk21 = a21.get("AIADMK Alliance", 0)
    aiadmk26 = a26.get("AIADMK Alliance", 0)
    tvk26 = int(w26[w26["winner_party"] == "TVK"]["winner_party"].count())
    total_flips = int(flip_df["is_flip"].sum())
    landslides26 = int((w26["winner_vote_share"] >= 50).sum())

    st.subheader("📊 Key Results at a Glance")
    cols = st.columns(5)
    with cols[0]:
        if st.button(f"🔴 DMK Alliance\n**{dmk26}** seats", key="nav_dmk", use_container_width=True):
            st.switch_page("pages/2_Geographic_Story.py")
        metric_card("DMK Alliance Seats", dmk26, delta=dmk26 - dmk21, delta_label="vs 2021")
    with cols[1]:
        if st.button(f"🟢 AIADMK Alliance\n**{aiadmk26}** seats", key="nav_aiadmk", use_container_width=True):
            st.switch_page("pages/2_Geographic_Story.py")
        metric_card("AIADMK Alliance Seats", aiadmk26, delta=aiadmk26 - aiadmk21, delta_label="vs 2021")
    with cols[2]:
        if st.button(f"🟠 TVK (New)\n**{tvk26}** seats", key="nav_tvk", use_container_width=True):
            st.switch_page("pages/4_Vote_Share_Story.py")
        metric_card("TVK Seats (New Party)", tvk26, delta=tvk26, delta_label="(0 in 2021)")
    with cols[3]:
        if st.button(f"🔄 Flipped\n**{total_flips}** constituencies", key="nav_flip", use_container_width=True):
            st.switch_page("pages/3_Flip_Story.py")
        metric_card("Constituencies Flipped", total_flips)
    with cols[4]:
        if st.button(f"🏆 Landslides\n**{landslides26}** wins", key="nav_margin", use_container_width=True):
            st.switch_page("pages/5_Margin_Story.py")
        metric_card("Landslide Wins (>50%)", landslides26)

    st.markdown("---")

    # ── SECTION 3: Drastic Changes Alert Panel ────────────────────────────────
    st.subheader("🚨 Significant Changes Detected: 2021 → 2026")
    try:
        alerts = detect_all_drastic_changes(w21, w26, vs, flip_df)
        high_alerts = [a for a in alerts if a.severity == "HIGH"]
        med_alerts = [a for a in alerts if a.severity == "MEDIUM"]

        st.markdown(
            f'<div style="background:#2a2a4a;padding:10px 16px;border-radius:8px;margin-bottom:12px;">'
            f'<b>{len(alerts)}</b> significant changes detected between 2021 and 2026 '
            f'<span style="color:#e94560;">({len(high_alerts)} HIGH, {len(med_alerts)} MEDIUM)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for alert in high_alerts:
            drastic_alert_box(alert.title, alert.body)
        for alert in med_alerts:
            st.warning(f"⚠️ **{alert.title}** — {alert.body}")
    except Exception as e:
        st.error(f"Alert detection error: {e}")

    st.markdown("---")

    # ── SECTION 4: Party Seat Count Bar Chart ─────────────────────────────────
    st.subheader("🏆 Seat Count: 2021 vs 2026")
    fig_seats = party_seat_bar_chart(w21, w26, min_seats=2)
    st.plotly_chart(fig_seats, use_container_width=True)

    # Download
    seats21 = w21.groupby("winner_party").size().rename("seats_2021")
    seats26 = w26.groupby("winner_party").size().rename("seats_2026")
    seats_df = pd.concat([seats21, seats26], axis=1).fillna(0).astype(int).reset_index()
    seats_df.columns = ["party", "seats_2021", "seats_2026"]
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button("⬇ Download seat data", seats_df.to_csv(index=False),
                       file_name=f"tn_election_seat_count_{ts}.csv", mime="text/csv")

    st.markdown("---")

    # ── SECTION 5: Alliance Donut Charts ──────────────────────────────────────
    st.subheader("🍩 Alliance Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(alliance_donut(w21, ALLIANCE_2021, 2021), use_container_width=True)
    with col2:
        st.plotly_chart(alliance_donut(w26, ALLIANCE_2026, 2026), use_container_width=True)

except Exception as e:
    st.error(f"Page error: {e}")
    with st.expander("Report Issue"):
        st.code(traceback.format_exc())

render_footer()
