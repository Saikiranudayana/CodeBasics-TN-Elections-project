"""pages/7_Map_View.py — Interactive alliance map for 2021 and 2026."""

import traceback
import pathlib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.styles import inject_css, STREAMLIT_CONFIG, top_nav, render_footer
from utils.data_loader import load_winners
from utils.constants import PARTY_COLORS

BASE_DIR = pathlib.Path(__file__).parent.parent
CONSTITUENCY_MASTER = BASE_DIR / "data" / "raw" / "constituency_master.csv"


@st.cache_data
def _district_map() -> pd.DataFrame:
    """Return ac_number → district mapping from constituency master."""
    return pd.read_csv(CONSTITUENCY_MASTER, usecols=["ac_number", "district"])


def enrich_with_district(winners: pd.DataFrame) -> pd.DataFrame:
    """Add 'district' column if not already present."""
    if "district" in winners.columns:
        return winners
    dm = _district_map()
    return winners.merge(dm, on="ac_number", how="left")

st.set_page_config(**STREAMLIT_CONFIG)
inject_css()
top_nav("map")
st.markdown('<hr style="margin:0;border:none;border-top:1px solid #1e1e1e;">', unsafe_allow_html=True)

# Alliance colour mapping
ALLIANCE_MAP = {
    "TVK": "TVK Alliance",
    "DMK": "DMK Alliance", "INC": "DMK Alliance",
    "CPI": "DMK Alliance", "CPI(M)": "DMK Alliance",
    "VCK": "DMK Alliance", "IUML": "DMK Alliance",
    "AIADMK": "AIADMK Alliance", "PMK": "AIADMK Alliance",
    "BJP": "AIADMK Alliance", "AMMK": "AIADMK Alliance",
}
ALLIANCE_COLORS = {
    "TVK Alliance":    "#e8845a",
    "DMK Alliance":    "#5a7a3a",
    "AIADMK Alliance": "#3aaa6a",
    "Others":          "#888888",
}

# TN district centroid lat/lon
DISTRICT_COORDS = {
    "Ariyalur":        (11.14, 79.08),
    "Chengalpattu":    (12.69, 79.98),
    "Chennai":         (13.09, 80.27),
    "Coimbatore":      (11.02, 76.96),
    "Cuddalore":       (11.75, 79.76),
    "Dharmapuri":      (12.12, 78.16),
    "Dindigul":        (10.36, 77.98),
    "Erode":           (11.34, 77.73),
    "Kallakurichi":    (11.74, 78.96),
    "Kanchipuram":     (12.84, 79.70),
    "Kanyakumari":     (8.12,  77.55),
    "Kanniyakumari":   (8.08,  77.54),
    "Karur":           (10.96, 78.08),
    "Krishnagiri":     (12.52, 78.22),
    "Madurai":         (9.93,  78.12),
    "Mayiladuthurai":  (11.10, 79.65),
    "Nagapattinam":    (10.76, 79.84),
    "Namakkal":        (11.22, 78.17),
    "Nilgiris":        (11.49, 76.73),
    "Perambalur":      (11.23, 78.88),
    "Pudukkottai":     (10.38, 78.82),
    "Ramanathapuram":  (9.37,  78.83),
    "Ranipet":         (12.93, 79.33),
    "Salem":           (11.65, 78.16),
    "Sivaganga":       (9.84,  78.48),
    "Tenkasi":         (8.96,  77.32),
    "Thanjavur":       (10.79, 79.14),
    "Theni":           (10.01, 77.48),
    "Thoothukudi":     (8.79,  78.14),
    "Tiruchirappalli": (10.80, 78.69),
    "Tirunelveli":     (8.73,  77.70),
    "Tirupattur":      (12.49, 78.57),
    "Tirupur":         (11.10, 77.34),
    "Tiruvallur":      (13.14, 79.91),
    "Tiruvannamalai":  (12.23, 79.07),
    "Tiruvarur":       (10.77, 79.64),
    "Vellore":         (12.92, 79.13),
    "Villupuram":      (11.94, 79.49),
    "Virudhunagar":    (9.58,  77.96),
}


@st.cache_data
def load_tn_geojson():
    """Load locally bundled TN district GeoJSON (downloaded once)."""
    import json
    p = BASE_DIR / "data" / "raw" / "tn_districts.geojson"
    if p.exists():
        return json.loads(p.read_text())
    return None


def get_alliance(party):
    return ALLIANCE_MAP.get(party, "Others")


def build_district_summary(winners):
    winners = winners.copy()
    winners["alliance"] = winners["winner_party"].apply(get_alliance)

    # Newer districts were carved from parent districts after 2011;
    # the constituency master still lists them under the parent.
    # Inherit the parent's dominant alliance so the map has no empty holes.
    DISTRICT_PARENT = {
        "Chengalpattu":  "Kanchipuram",
        "Kallakurichi":  "Villupuram",
        "Mayiladuthurai":"Nagapattinam",
        "Ranipet":       "Vellore",
        "Tenkasi":       "Tirunelveli",
        "Tirupattur":    "Krishnagiri",
    }

    rows = []
    for dist, grp in winners.groupby("district"):
        ally_counts = grp["alliance"].value_counts()
        dom = ally_counts.idxmax()
        lat, lon = DISTRICT_COORDS.get(dist, (None, None))
        rows.append({
            "district":    dist,
            "dominant":    dom,
            "color":       ALLIANCE_COLORS[dom],
            "TVK_seats":   int((grp["alliance"] == "TVK Alliance").sum()),
            "DMK_seats":   int((grp["alliance"] == "DMK Alliance").sum()),
            "ADMK_seats":  int((grp["alliance"] == "AIADMK Alliance").sum()),
            "Other_seats": int((grp["alliance"] == "Others").sum()),
            "total_seats": len(grp),
            "lat": lat,
            "lon": lon,
        })

    # Build lookup for filled rows
    dist_lookup = {r["district"]: r for r in rows}

    # Add inherited rows for newer districts missing from data
    for child, parent in DISTRICT_PARENT.items():
        if child not in dist_lookup and parent in dist_lookup:
            p = dist_lookup[parent]
            lat, lon = DISTRICT_COORDS.get(child, (p["lat"], p["lon"]))
            rows.append({
                "district":    child,
                "dominant":    p["dominant"],
                "color":       p["color"],
                "TVK_seats":   0,
                "DMK_seats":   0,
                "ADMK_seats":  0,
                "Other_seats": 0,
                "total_seats": 0,
                "lat": lat,
                "lon": lon,
                "_inherited": True,
            })

    return pd.DataFrame(rows)


def build_constituency_table(winners):
    w = winners.copy()
    w["alliance"] = w["winner_party"].apply(get_alliance)
    return w[["ac_number","constituency","district","winner_party","alliance",
              "winner_votes","margin","winner_vote_share","reserved"]].copy()


def make_main_map(geojson, dist_df, year):
    """Choropleth mapbox — only TN, no labels, hover on mouse-over."""
    df = dist_df.copy()
    alliance_order = ["TVK Alliance", "DMK Alliance", "AIADMK Alliance", "Others"]

    # Custom hover template
    def _hover(r):
        header = (
            f"<b>{r['district']}</b><br>"
            f"<span style='color:#aaa'>Dominant:</span> <b>{r['dominant']}</b><br>"
        )
        if r.get("total_seats", 0) > 0:
            body = (
                f"TVK Alliance &nbsp;&nbsp;: {r['TVK_seats']} seats<br>"
                f"DMK Alliance &nbsp;&nbsp;: {r['DMK_seats']} seats<br>"
                f"AIADMK Alliance : {r['ADMK_seats']} seats<br>"
                f"Others &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: {r['Other_seats']} seats<br>"
                f"<b>Total : {r['total_seats']} seats</b>"
            )
        else:
            body = "<i style='color:#888'>Newer district — colour inherited<br>from parent district</i>"
        return header + body

    df["hover_text"] = df.apply(_hover, axis=1)

    if geojson:
        fig = px.choropleth_mapbox(
            df,
            geojson=geojson,
            locations="district",
            featureidkey="properties.district",
            color="dominant",
            color_discrete_map=ALLIANCE_COLORS,
            category_orders={"dominant": alliance_order},
            custom_data=["hover_text"],
            mapbox_style="carto-darkmatter",
            zoom=6.1,
            center={"lat": 10.8, "lon": 78.65},
            opacity=0.82,
        )
        fig.update_traces(
            hovertemplate="%{customdata[0]}<extra></extra>",
            marker_line_width=0.8,
            marker_line_color="#1a1a1a",
        )
    else:
        # Fallback: bubble scatter on dark OSM
        df2 = df.dropna(subset=["lat", "lon"])
        fig = go.Figure()
        for alliance, color in ALLIANCE_COLORS.items():
            sub = df2[df2["dominant"] == alliance]
            if sub.empty:
                continue
            fig.add_trace(go.Scattermapbox(
                lat=sub["lat"], lon=sub["lon"],
                mode="markers",
                marker=dict(size=sub["total_seats"] * 3.5, color=color,
                            opacity=0.85, sizemode="diameter"),
                hovertext=sub["hover_text"],
                hoverinfo="text",
                name=alliance,
            ))
        fig.update_layout(mapbox=dict(
            style="open-street-map",
            center=dict(lat=10.8, lon=78.7), zoom=6.1,
        ))

    fig.update_layout(
        title=dict(
            text=f"{year} TN Election — Alliance Dominance by District",
            font=dict(color="#ffffff", size=16),
        ),
        template="plotly_dark",
        paper_bgcolor="#0d0d0d",
        legend=dict(
            title="Alliance",
            bgcolor="#111",
            bordercolor="#333",
            borderwidth=1,
            font=dict(color="#ccc"),
        ),
        hoverlabel=dict(bgcolor="#1e1e1e", font_color="#ffffff", font_size=13),
        height=680,
        margin=dict(t=50, b=0, l=0, r=0),
    )
    return fig


# ── Main page ──────────────────────────────────────────────────────────────
try:
    st.title("🗺️ Districtwise Map View")
    st.caption("District-wise alliance dominance for 2021 and 2026 elections.")

    year_tab = st.radio("Select election year:", ["2026","2021","Side-by-side"], horizontal=True)

    with st.spinner("Loading election data…"):
        w21 = enrich_with_district(load_winners(2021))
        w26 = enrich_with_district(load_winners(2026))

    with st.spinner("Loading map data…"):
        geojson = load_tn_geojson()

    dist21 = build_district_summary(w21)
    dist26 = build_district_summary(w26)

    # Legend
    legend_html = "".join(
        f'<span style="display:inline-flex;align-items:center;margin-right:24px;">'
        f'<span style="width:14px;height:14px;border-radius:50%;background:{c};'
        f'display:inline-block;margin-right:6px;"></span>'
        f'<span style="font-size:13px;color:#ccc;">{n}</span></span>'
        for n, c in ALLIANCE_COLORS.items()
    )
    st.markdown(f'<div style="margin:8px 0 16px;">{legend_html}</div>', unsafe_allow_html=True)

    def render_map(dist_df, year):
        fig = make_main_map(geojson, dist_df, year)
        st.plotly_chart(fig, use_container_width=True)

    if year_tab == "2026":
        render_map(dist26, 2026)
    elif year_tab == "2021":
        render_map(dist21, 2021)
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("2021")
            f21 = make_main_map(geojson, dist21, 2021)
            f21.update_layout(height=500, title=dict(text=""))
            st.plotly_chart(f21, use_container_width=True)
        with col2:
            st.subheader("2026")
            f26 = make_main_map(geojson, dist26, 2026)
            f26.update_layout(height=500, title=dict(text=""))
            st.plotly_chart(f26, use_container_width=True)

    st.markdown("---")

    # District summary table
    st.subheader("District-wise Alliance Summary")
    tab_sel = st.radio("Year for table:", ["2026","2021"], horizontal=True, key="tbl_year")
    tbl_df = dist26 if tab_sel == "2026" else dist21

    def style_dominant(val):
        c = ALLIANCE_COLORS.get(val, "#888")
        return f"background-color:{c}22; color:{c}; font-weight:600;"

    styled_tbl = (
        tbl_df[["district","dominant","TVK_seats","DMK_seats","ADMK_seats","Other_seats","total_seats"]]
        .rename(columns={"district":"District","dominant":"Dominant Alliance",
                         "TVK_seats":"TVK+","DMK_seats":"DMK+","ADMK_seats":"ADMK+",
                         "Other_seats":"Others","total_seats":"Total"})
        .sort_values("Total", ascending=False)
        .style.applymap(style_dominant, subset=["Dominant Alliance"])
    )
    st.dataframe(styled_tbl, use_container_width=True, height=500)

    st.markdown("---")

    # Constituency detail
    st.subheader("Constituency-level Detail")
    detail_year = st.radio("Year:", ["2026","2021"], horizontal=True, key="detail_year")
    detail_df = build_constituency_table(w26 if detail_year == "2026" else w21)
    selected_district = st.selectbox("Filter by district:", ["All"] + sorted(detail_df["district"].unique().tolist()))
    if selected_district != "All":
        detail_df = detail_df[detail_df["district"] == selected_district]

    def color_alliance(val):
        c = ALLIANCE_COLORS.get(val, "#888")
        return f"color:{c}; font-weight:600;"

    styled_detail = (
        detail_df[["ac_number","constituency","district","winner_party","alliance",
                   "winner_votes","margin","winner_vote_share","reserved"]]
        .rename(columns={"ac_number":"#","constituency":"Constituency","district":"District",
                         "winner_party":"Party","alliance":"Alliance","winner_votes":"Votes",
                         "margin":"Margin","winner_vote_share":"Vote %","reserved":"Type"})
        .style.applymap(color_alliance, subset=["Alliance"])
    )
    st.dataframe(styled_detail, use_container_width=True, height=450)

except Exception as e:
    st.error(f"Map page error: {e}")
    with st.expander("Error details"):
        st.code(traceback.format_exc())

render_footer()
