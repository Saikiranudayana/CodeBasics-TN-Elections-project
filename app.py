"""app.py — TN Election 2026 Dashboard home page."""

import subprocess
import sys
import pathlib
import streamlit as st

from components.styles import STREAMLIT_CONFIG, inject_css, top_nav
st.set_page_config(**STREAMLIT_CONFIG)

from utils.data_loader import (
    load_winners, load_vote_share, load_flip_seats,
    processed_files_exist, get_pipeline_timestamp,
)
from utils.constants import ALLIANCE_2026

inject_css()

BASE_DIR = pathlib.Path(__file__).parent

# ── Check processed data exists ───────────────────────────────────────────────
if not processed_files_exist():
    st.warning("⚠️ Processed data not found. Run: `python pipeline/run_pipeline.py`")
    if st.button("▶ Run Data Pipeline Now"):
        with st.spinner("Running pipeline…"):
            result = subprocess.run(
                [sys.executable, str(BASE_DIR / "pipeline" / "run_pipeline.py")],
                capture_output=True, text=True, cwd=str(BASE_DIR),
            )
        if result.returncode == 0:
            st.success("Pipeline completed! Reload the page.")
        else:
            st.error("Pipeline failed:"); st.code(result.stderr)
    st.stop()

# ── Load data ─────────────────────────────────────────────────────────────────
w26 = load_winners(2026)
w21 = load_winners(2021)
flip_df = load_flip_seats()

# ── Top Nav ───────────────────────────────────────────────────────────────────
top_nav("home")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

# ── Compute key numbers ───────────────────────────────────────────────────────
party_seats = w26.groupby("winner_party").size().to_dict()
tvk_seats  = party_seats.get("TVK", 0)
dmk_solo   = party_seats.get("DMK", 0)
aiadmk_solo = party_seats.get("AIADMK", 0)

spk_parties  = ["DMK", "INC", "CPI", "CPI(M)", "VCK", "IUML"]
nda_parties  = ["AIADMK", "PMK", "BJP", "AMMK"]
spk_seats    = sum(party_seats.get(p, 0) for p in spk_parties)
nda_seats    = sum(party_seats.get(p, 0) for p in nda_parties)

total_candidates = 4023   # from raw CSV count
total_parties    = 106
total_electors_cr = 5.73
voters_polled    = 48798833
turnout_pct      = 85.10

# ── Hero Section ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-section">
  <div class="hero-badge">🏆 Historic Milestone</div>
  <h1 class="hero-headline">Vijay's <span class="tvk-highlight">TVK</span> wins {tvk_seats} seats in first election</h1>
  <p class="hero-sub">A new political era begins as the debutant party secures a historic mandate across Tamil Nadu.</p>
</div>
""", unsafe_allow_html=True)

# ── Party Scorecards ──────────────────────────────────────────────────────────
st.markdown(f"""
<div class="party-tally-row">
  <div class="party-tally-card tvk">
    <div class="party-tally-label">TVK</div>
    <div class="party-tally-number">{tvk_seats}</div>
    <div class="party-tally-sub">seats</div>
  </div>
  <div class="party-tally-card dmk">
    <div class="party-tally-label">DMK<sup style="font-size:10px">+</sup></div>
    <div class="party-tally-number">{spk_seats}</div>
    <div class="party-tally-sub">seats (SPK alliance)</div>
  </div>
  <div class="party-tally-card admk">
    <div class="party-tally-label">ADMK<sup style="font-size:10px">+</sup></div>
    <div class="party-tally-number">{nda_seats}</div>
    <div class="party-tally-sub">seats (NDA alliance)</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Summary Stats Bar ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="stats-bar">
  <div class="stat-cell">
    <div class="stat-cell-label">Total Seats</div>
    <div class="stat-cell-value">234</div>
    <div class="stat-cell-sub">Assembly constituencies</div>
  </div>
  <div class="stat-cell">
    <div class="stat-cell-label">Candidates</div>
    <div class="stat-cell-value">{total_candidates:,}</div>
    <div class="stat-cell-sub">Across all parties</div>
  </div>
  <div class="stat-cell">
    <div class="stat-cell-label">Parties</div>
    <div class="stat-cell-value">{total_parties}</div>
    <div class="stat-cell-sub">Contested</div>
  </div>
  <div class="stat-cell">
    <div class="stat-cell-label">Electors</div>
    <div class="stat-cell-value">{total_electors_cr} Cr</div>
    <div class="stat-cell-sub">5,73,43,291 registered</div>
  </div>
  <div class="stat-cell">
    <div class="stat-cell-label">Voters Polled</div>
    <div class="stat-cell-value">{voters_polled:,}</div>
    <div class="stat-cell-sub">Total voters polled</div>
  </div>
  <div class="stat-cell">
    <div class="stat-cell-label">Voter Turnout</div>
    <div class="stat-cell-value green">{turnout_pct:.2f}%</div>
    <div class="stat-cell-sub">72.7% in 2021</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Navigation Feature Cards ──────────────────────────────────────────────────
st.markdown("""
<div class="nav-cards-grid">
  <div class="nav-card blue">
    <div>
      <p class="nav-card-title">Election Results</p>
      <p class="nav-card-sub">View the full constituency-wise list of winning candidates, margins, and party standings.</p>
    </div>
    <div class="nav-card-footer">
      <span class="nav-card-icon">🗳️</span>
      <span class="nav-card-cta">View Results →</span>
    </div>
  </div>
  <div class="nav-card purple">
    <div>
      <p class="nav-card-title">Regional Analysis</p>
      <p class="nav-card-sub">Analyse the election outcome grouped by region to understand geographic dominance.</p>
    </div>
    <div class="nav-card-footer">
      <span class="nav-card-icon">🗺️</span>
      <span class="nav-card-cta">View Regions →</span>
    </div>
  </div>
  <div class="nav-card teal">
    <div>
      <p class="nav-card-title">Vote Share Story</p>
      <p class="nav-card-sub">Deep dive into party vote share trends and TVK's historic debut performance.</p>
    </div>
    <div class="nav-card-footer">
      <span class="nav-card-icon">📊</span>
      <span class="nav-card-cta">Explore →</span>
    </div>
  </div>
</div>
<div style="height:2px"></div>
<div class="nav-cards-grid-2">
  <div class="nav-card green">
    <div>
      <p class="nav-card-title">Constituency Flip Tracker</p>
      <p class="nav-card-sub">Search and discover which constituencies changed hands between 2021 and 2026.</p>
    </div>
    <div class="nav-card-footer">
      <span class="nav-card-icon">🔄</span>
      <span class="nav-card-cta">Explore Flips →</span>
    </div>
  </div>
  <div class="nav-card dark">
    <div>
      <p class="nav-card-title">Margin &amp; Reserved Seats</p>
      <p class="nav-card-sub">Analyse victory margins, narrow wins, and reserved seat breakdown by category.</p>
    </div>
    <div class="nav-card-footer">
      <span class="nav-card-icon">📏</span>
      <span class="nav-card-cta">View Stats →</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Interactive page link buttons under cards ─────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.page_link("pages/1_Overview.py", label="🗳️ Election Results", use_container_width=True)
with c2:
    st.page_link("pages/2_Geographic_Story.py", label="🗺️ Regional Analysis", use_container_width=True)
with c3:
    st.page_link("pages/4_Vote_Share_Story.py", label="📊 Vote Share", use_container_width=True)
with c4:
    st.page_link("pages/3_Flip_Story.py", label="🔄 Flip Tracker", use_container_width=True)
with c5:
    st.page_link("pages/5_Margin_Story.py", label="📏 Margins & Reserved", use_container_width=True)

# ── Quick Stats Row ──────────────────────────────────────────────────────────
st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
st.markdown("#### 📊 Quick Stats at a Glance")
qs1, qs2, qs3, qs4, qs5 = st.columns(5)
total_flips = int(flip_df["is_flip"].sum())
landslides  = int((w26["winner_vote_share"] >= 50).sum())
narrow_wins = int((w26["margin_pct"] < 2).sum())
avg_margin  = w26["margin"].mean()
dmk21_seats = (w21["winner_party"] == "DMK").sum()

qs1.metric("DMK Standalone", dmk_solo, delta=int(dmk_solo - dmk21_seats), help="DMK party seats (not alliance)")
qs2.metric("Constituencies Flipped", total_flips, help="Seat changed party from 2021 to 2026")
qs3.metric("Landslide Wins (>50%)", landslides, help="Winner got >50% of total votes")
qs4.metric("Narrow Wins (<2%)", narrow_wins, help="Margin of victory < 2% of valid votes")
qs5.metric("Avg Margin of Victory", f"{avg_margin:,.0f}", help="Average winning margin in votes")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
  <p>Data sourced from Election Commission of India · For informational purposes only · 2026</p>
  <p style="color:#555;font-size:11px;">Built with Streamlit + Plotly &nbsp;|&nbsp;
  Designed &amp; Developed by <a href="https://www.linkedin.com/in/saikiranudayana/" target="_blank"
  style="color:#0a66c2;text-decoration:none;font-weight:600;">Saikiran Udayana</a></p>
</div>
""", unsafe_allow_html=True)
