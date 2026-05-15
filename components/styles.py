"""components/styles.py — Shared CSS and theme configuration."""

import streamlit as st

STREAMLIT_CONFIG = {
    "page_title": "2026 TN Elections",
    "layout": "wide",
    "page_icon": "🗳️",
    "initial_sidebar_state": "collapsed",
}


def inject_css():
    """Inject custom CSS into the Streamlit app."""
    st.markdown(
        """
        <style>
        /* ── Global ─────────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0d0d0d;
            color: #e0e0e0;
        }
        [data-testid="stHeader"] { display: none !important; }
        [data-testid="stDecoration"] { display: none !important; }
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        .block-container { padding-top: 0 !important; max-width: 1400px; }

        /* ── Top Navigation Bar ─────────────────────────── */
        .topnav {
            background: #111111;
            border-bottom: 1px solid #222;
            padding: 20px 16px 8px 16px;
            display: flex;
            align-items: center;
            gap: 0px;
            position: sticky;
            top: 0;
            z-index: 999;
            margin-bottom: 0;
            flex-wrap: nowrap;
        }
        .topnav-logo {
            font-weight: 800;
            font-size: 13px;
            color: #ffffff;
            margin-right: 12px;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }
        .topnav-logo span { color: #f5a623; }
        .nav-link {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 10px 11px;
            font-size: 12.5px;
            font-weight: 500;
            color: #aaaaaa;
            text-decoration: none;
            border-bottom: 2px solid transparent;
            transition: color 0.2s, border-color 0.2s;
            cursor: pointer;
            white-space: nowrap;
        }
        .nav-link:hover { color: #ffffff; }
        .nav-link.active { color: #ffffff; border-bottom-color: #ffffff; }

        /* ── Hero Section ───────────────────────────────── */
        .hero-section {
            background: linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.85) 100%),
                        linear-gradient(135deg, #1a0a00 0%, #2d1500 40%, #0a0a0a 100%);
            border-radius: 0;
            padding: 60px 40px 40px;
            position: relative;
            overflow: hidden;
            margin-bottom: 0;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(245,166,35,0.15);
            border: 1px solid rgba(245,166,35,0.4);
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 11px;
            font-weight: 700;
            color: #f5a623;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 16px;
        }
        .hero-headline {
            font-size: 36px;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.2;
            margin: 0 0 10px;
        }
        .hero-headline .tvk-highlight { color: #f5a623; }
        .hero-sub {
            font-size: 15px;
            color: #888888;
            margin: 0;
        }

        /* ── Party Scorecards ───────────────────────────── */
        .party-tally-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1px;
            background: #222;
            margin: 0;
        }
        .party-tally-card {
            padding: 20px 24px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .party-tally-card.tvk { background: #1a1200; }
        .party-tally-card.dmk { background: #1a0505; }
        .party-tally-card.admk { background: #051a0a; }
        .party-tally-label {
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }
        .party-tally-card.tvk .party-tally-label { color: #f5a623; }
        .party-tally-card.dmk .party-tally-label { color: #e31e24; }
        .party-tally-card.admk .party-tally-label { color: #00853f; }
        .party-tally-number {
            font-size: 48px;
            font-weight: 900;
            line-height: 1;
        }
        .party-tally-card.tvk .party-tally-number { color: #f5a623; }
        .party-tally-card.dmk .party-tally-number { color: #e31e24; }
        .party-tally-card.admk .party-tally-number { color: #00853f; }
        .party-tally-sub { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }

        /* ── Summary Stats Bar ──────────────────────────── */
        .stats-bar {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 1px;
            background: #1a1a1a;
            border-top: 1px solid #222;
            border-bottom: 1px solid #222;
        }
        .stat-cell {
            background: #111111;
            padding: 14px 16px;
        }
        .stat-cell-label {
            font-size: 10px;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 4px;
        }
        .stat-cell-value {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
        }
        .stat-cell-sub { font-size: 10px; color: #444; margin-top: 2px; }
        .stat-cell-value.green { color: #4caf50; }

        /* ── Navigation Feature Cards ───────────────────── */
        .nav-cards-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2px;
            background: #0d0d0d;
            padding: 2px 0;
        }
        .nav-cards-grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2px;
            background: #0d0d0d;
        }
        .nav-card {
            padding: 28px 24px 22px;
            border-radius: 0;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            min-height: 130px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: filter 0.2s ease;
        }
        .nav-card:hover { filter: brightness(1.1); }
        .nav-card.blue { background: linear-gradient(135deg, #1a4fd8, #2563eb); }
        .nav-card.purple { background: linear-gradient(135deg, #7c3aed, #9333ea); }
        .nav-card.teal { background: linear-gradient(135deg, #0891b2, #06b6d4); }
        .nav-card.green { background: linear-gradient(135deg, #059669, #10b981); }
        .nav-card.dark { background: linear-gradient(135deg, #1f2937, #374151); }
        .nav-card-title {
            font-size: 18px;
            font-weight: 700;
            color: #ffffff;
            margin: 0;
        }
        .nav-card-sub {
            font-size: 12px;
            color: rgba(255,255,255,0.7);
            margin-top: 6px;
        }
        .nav-card-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 16px;
        }
        .nav-card-icon {
            font-size: 20px;
            opacity: 0.8;
        }
        .nav-card-cta {
            font-size: 11px;
            font-weight: 600;
            color: rgba(255,255,255,0.8);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* ── Metric Card (smaller inline stats) ─────────── */
        .metric-card {
            background: #161616;
            border-radius: 10px;
            padding: 16px 18px;
            border-left: 3px solid #e94560;
            margin-bottom: 12px;
        }
        .metric-card h3 { color: #777; font-size: 12px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-card .value { color: #ffffff; font-size: 26px; font-weight: 800; }
        .metric-card .delta { font-size: 12px; margin-top: 4px; }
        .delta-pos { color: #4caf50; }
        .delta-neg { color: #f44336; }

        /* ── Party badge ─────────────────────────────────── */
        .party-badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            color: white;
        }

        /* ── Drastic alert ───────────────────────────────── */
        .drastic-alert {
            background: linear-gradient(135deg, #e94560, #0f3460);
            border-radius: 8px;
            padding: 14px 18px;
            color: white;
            font-weight: bold;
            animation: pulse 2s infinite;
            margin-bottom: 10px;
        }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.75} }

        /* ── Scrollbar ───────────────────────────────────── */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #111; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }

        /* ── Tables ──────────────────────────────────────── */
        .results-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .results-table th {
            background: #1a1a1a;
            color: #777;
            padding: 10px 12px;
            text-align: left;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #222;
        }
        .results-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #1a1a1a;
            color: #ddd;
        }
        .results-table tr:hover td { background: #161616; }
        .results-table .const-name { font-weight: 600; color: #fff; }
        .results-table .const-dist { font-size: 11px; color: #555; }

        /* ── Constituency card ───────────────────────────── */
        .const-card {
            background: #111111;
            border: 1px solid #1e1e1e;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 8px;
            transition: border-color 0.2s;
        }
        .const-card:hover { border-color: #333; }
        .const-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
        }
        .const-card-name { font-weight: 700; font-size: 14px; color: #fff; }
        .const-card-meta { font-size: 11px; color: #555; margin-top: 2px; }
        .cat-badge {
            display: inline-block;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
            background: #1e1e1e;
            color: #888;
            margin-left: 4px;
        }
        .cat-badge.sc { background: rgba(245,166,35,0.1); color: #f5a623; }
        .cat-badge.st { background: rgba(139,92,246,0.1); color: #8b5cf6; }
        .cat-badge.gen { background: rgba(99,102,241,0.1); color: #6366f1; }
        .ac-number { font-size: 10px; color: #444; }

        /* ── Election banner (legacy) ────────────────────── */
        .election-banner {
            background: linear-gradient(135deg, #0f3460, #16213e);
            border-radius: 10px;
            padding: 20px 28px;
            color: white;
            margin-bottom: 20px;
            border-left: 5px solid #e94560;
        }
        .election-banner h1 { font-size: 24px; margin: 0; color: white; }
        .election-banner p { font-size: 14px; color: #a0a0c0; margin: 6px 0 0 0; }

        /* ── Spotlight card ──────────────────────────────── */
        .spotlight-card {
            background: #161616;
            border-radius: 8px;
            padding: 14px 16px;
            border-top: 3px solid #e94560;
            margin-bottom: 10px;
        }

        /* ── Flip highlight ──────────────────────────────── */
        .flip-row { background-color: rgba(233,69,96,0.08); }

        /* ── Footer ──────────────────────────────────────── */
        .site-footer {
            background: #0a0a0a;
            border-top: 1px solid #1a1a1a;
            padding: 24px;
            text-align: center;
        }
        .site-footer p { color: #333; font-size: 12px; margin: 4px 0; }
        .footer { text-align:center; color:#555; font-size:12px; padding:16px; border-top:1px solid #1e1e1e; margin-top:32px; }

        /* ── Party filter pills ──────────────────────────── */
        .party-pill {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
            border: 1px solid #222;
            background: #161616;
            color: #aaa;
            margin: 2px;
        }
        .party-pill .pill-dot { width: 8px; height: 8px; border-radius: 50%; }
        .party-pill .pill-count { color: #555; font-weight: 400; }

        /* Streamlit button overrides for nav links */
        [data-testid="stPageLink-NavLink"] {
            background: transparent !important;
            border: none !important;
            color: #aaa !important;
            padding: 14px 16px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            border-radius: 0 !important;
        }
        [data-testid="stPageLink-NavLink"]:hover {
            background: transparent !important;
            color: #fff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    """Render the standard footer with data source and developer credit."""
    st.markdown(
        '<div class="footer">'
        'Data source: Election Commission of India | Built for AtliQ Media<br>'
        '<span style="font-size:11px;color:#666;">Designed &amp; Developed by '
        '<a href="https://www.linkedin.com/in/saikiranudayana/" target="_blank" '
        'style="color:#0a66c2;text-decoration:none;font-weight:600;">Saikiran Udayana</a>'
        '</span></div>',
        unsafe_allow_html=True,
    )


def top_nav(active_page: str = "home"):
    """Render a top navigation bar as pure HTML – no truncation."""
    pages = [
        ("home",     "🏠", "Home",      "/"),
        ("results",  "🗳️", "Results",   "/Overview"),
        ("map",      "🗺️", "Map View",  "/Map_View"),
        ("geo",      "📍", "Regional",  "/Geographic_Story"),
        ("flip",     "🔄", "Flips",     "/Flip_Story"),
        ("vote",     "📊", "Vote %",    "/Vote_Share_Story"),
        ("margin",   "📏", "Margins",   "/Margin_Story"),
        ("reserved", "⚖️", "Reserved",  "/Reserved_Seats"),
    ]

    links_html = ""
    for key, icon, label, url in pages:
        active_class = " active" if key == active_page else ""
        links_html += (
            f'<a href="{url}" class="nav-link{active_class}" '
            f'style="white-space:nowrap;">{icon}&nbsp;{label}</a>'
        )

    nav_html = (
        '<div class="topnav" style="flex-wrap:nowrap;overflow-x:auto;">'
        '<div class="topnav-logo" style="min-width:max-content;">'
        '🗳️ <span style="color:#f5a623;">2026</span>&nbsp;TN&nbsp;ELECTIONS'
        '</div>'
        + links_html +
        '</div>'
    )
    st.markdown(nav_html, unsafe_allow_html=True)

