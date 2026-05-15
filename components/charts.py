"""components/charts.py — Reusable Plotly chart functions."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from utils.constants import PARTY_COLORS, REGION_ORDER, MAJORITY_MARK


def get_color(party: str) -> str:
    return PARTY_COLORS.get(party, "#CCCCCC")


def party_seat_bar_chart(w21: pd.DataFrame, w26: pd.DataFrame, min_seats: int = 2) -> go.Figure:
    """Horizontal grouped bar chart: party seats 2021 vs 2026."""
    seats21 = w21.groupby("winner_party").size().rename("2021")
    seats26 = w26.groupby("winner_party").size().rename("2026")
    df = pd.concat([seats21, seats26], axis=1).fillna(0).astype(int)
    df = df[(df["2021"] >= min_seats) | (df["2026"] >= min_seats)]
    df = df.sort_values("2026", ascending=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=df.index, x=df["2021"], name="2021",
        orientation="h", marker_color="#4a90d9",
        text=df["2021"], textposition="auto",
    ))
    fig.add_trace(go.Bar(
        y=df.index, x=df["2026"], name="2026",
        orientation="h", marker_color="#e94560",
        text=df["2026"], textposition="auto",
    ))
    fig.add_vline(x=MAJORITY_MARK, line_dash="dash", line_color="gold",
                  annotation_text=f"Majority ({MAJORITY_MARK})", annotation_position="top right")
    fig.update_layout(
        title="Seat Count: 2021 vs 2026",
        barmode="group",
        template="plotly_dark",
        height=max(400, len(df) * 40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        xaxis_title="Seats Won",
    )
    return fig


def alliance_donut(w: pd.DataFrame, alliance_map: dict, year: int) -> go.Figure:
    """Donut chart for alliance seat distribution."""
    party_seats = w.groupby("winner_party").size().to_dict()
    labels, values, colors = [], [], []
    palette = ["#e94560", "#4a90d9", "#f39c12", "#2ecc71", "#9b59b6", "#cccccc"]

    for i, (alliance, parties) in enumerate(alliance_map.items()):
        seats = sum(party_seats.get(p, 0) for p in parties)
        if seats > 0:
            labels.append(alliance)
            values.append(seats)
            colors.append(palette[i % len(palette)])

    others = sum(s for p, s in party_seats.items()
                 if not any(p in ps for ps in alliance_map.values()))
    if others > 0:
        labels.append("Others")
        values.append(others)
        colors.append("#888888")

    winning = labels[values.index(max(values))] if values else ""
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker_colors=colors,
        textinfo="label+value",
    ))
    fig.update_layout(
        title=f"{year} Alliance Results",
        template="plotly_dark",
        annotations=[dict(text=f"{winning}<br>{max(values) if values else 0}", x=0.5, y=0.5,
                          font_size=13, showarrow=False, font_color="white")],
        height=350,
        showlegend=True,
    )
    return fig


def region_seat_heatmap(w: pd.DataFrame, major_parties: list) -> go.Figure:
    """Grouped bar chart: seats by region and party."""
    df = w[w["winner_party"].isin(major_parties)].copy()
    df_grp = df.groupby(["region", "winner_party"]).size().reset_index(name="seats")

    fig = px.bar(
        df_grp, x="region", y="seats", color="winner_party",
        barmode="group",
        category_orders={"region": REGION_ORDER, "winner_party": major_parties},
        color_discrete_map=PARTY_COLORS,
        title="Seats by Region and Party",
    )
    fig.update_layout(template="plotly_dark", height=400,
                      xaxis_title="Region", yaxis_title="Seats")
    return fig


def sankey_flip(flip_df: pd.DataFrame) -> go.Figure:
    """Sankey diagram showing seat flows from 2021 to 2026 parties."""
    flipped = flip_df[flip_df["is_flip"]].copy()

    # Aggregate flows
    flows = flipped.groupby(["winner_party_2021", "winner_party_2026"]).size().reset_index(name="count")
    flows = flows[flows["count"] >= 3]

    # Build node list
    sources_21 = flows["winner_party_2021"].unique().tolist()
    targets_26 = flows["winner_party_2026"].unique().tolist()
    all_nodes = []
    for p in sources_21:
        all_nodes.append(f"{p} (2021)")
    for p in targets_26:
        if f"{p} (2026)" not in all_nodes:
            all_nodes.append(f"{p} (2026)")

    node_idx = {n: i for i, n in enumerate(all_nodes)}
    source_indices, target_indices, values, link_colors = [], [], [], []
    for _, row in flows.iterrows():
        s = node_idx.get(f"{row['winner_party_2021']} (2021)")
        t = node_idx.get(f"{row['winner_party_2026']} (2026)")
        if s is not None and t is not None:
            source_indices.append(s)
            target_indices.append(t)
            values.append(int(row["count"]))
            c = PARTY_COLORS.get(row["winner_party_2021"], "#888888")
            link_colors.append(c + "99")

    node_colors = []
    for n in all_nodes:
        party = n.split(" (")[0]
        node_colors.append(PARTY_COLORS.get(party, "#888888"))

    fig = go.Figure(go.Sankey(
        node=dict(label=all_nodes, color=node_colors, pad=15, thickness=20),
        link=dict(source=source_indices, target=target_indices, value=values, color=link_colors),
    ))
    fig.update_layout(
        title="Where did seats go? 2021 → 2026 seat flows",
        template="plotly_dark", height=500,
    )
    return fig


def margin_histogram(w21: pd.DataFrame, w26: pd.DataFrame) -> go.Figure:
    """Overlaid histogram of winning margin percentages."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=w21["margin_pct"], name="2021",
        opacity=0.6, marker_color="#4a90d9", nbinsx=30,
    ))
    fig.add_trace(go.Histogram(
        x=w26["margin_pct"], name="2026",
        opacity=0.6, marker_color="#e94560", nbinsx=30,
    ))
    for thresh, label in [(2, "2%"), (10, "10%"), (25, "25%")]:
        fig.add_vline(x=thresh, line_dash="dot", line_color="gold",
                      annotation_text=label, annotation_position="top")
    fig.update_layout(
        title="Distribution of Winning Margins",
        barmode="overlay",
        template="plotly_dark",
        xaxis_title="Margin %",
        yaxis_title="Number of Constituencies",
        height=400,
    )
    return fig


def margin_scatter(margin_df: pd.DataFrame) -> go.Figure:
    """Scatter: margin 2021 vs 2026, coloured by flip status."""
    margin_df = margin_df.copy()
    margin_df["flipped"] = margin_df["winner_party_2021"] != margin_df["winner_party_2026"]
    margin_df["color"] = margin_df["flipped"].map({True: "#e94560", False: "#4a90d9"})
    margin_df["status"] = margin_df["flipped"].map({True: "Flipped", False: "Retained"})

    fig = px.scatter(
        margin_df, x="margin_pct_2021", y="margin_pct_2026",
        color="status",
        color_discrete_map={"Flipped": "#e94560", "Retained": "#4a90d9"},
        hover_data={"constituency": True, "winner_party_2021": True, "winner_party_2026": True},
        title="Margin of Victory: 2021 vs 2026",
    )
    # Add diagonal reference line
    max_val = max(margin_df["margin_pct_2021"].max(), margin_df["margin_pct_2026"].max())
    fig.add_trace(go.Scatter(
        x=[0, max_val], y=[0, max_val],
        mode="lines", line=dict(color="gold", dash="dash"),
        name="Same margin both years", showlegend=True,
    ))
    fig.update_layout(template="plotly_dark", height=500,
                      xaxis_title="Margin % 2021", yaxis_title="Margin % 2026")
    return fig


def vote_share_diverging(vs21_state: pd.DataFrame, vs26_state: pd.DataFrame,
                         major_parties: list) -> go.Figure:
    """Diverging bar chart: 2021 left (negative), 2026 right (positive)."""
    df21 = vs21_state[vs21_state["party"].isin(major_parties)].set_index("party")["vote_share_pct"]
    df26 = vs26_state[vs26_state["party"].isin(major_parties)].set_index("party")["vote_share_pct"]
    all_p = sorted(major_parties, key=lambda p: df26.get(p, 0), reverse=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=all_p, x=[-df21.get(p, 0) for p in all_p], name="2021",
        orientation="h", marker_color="#4a90d9",
        text=[f"{df21.get(p, 0):.1f}%" for p in all_p], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        y=all_p, x=[df26.get(p, 0) for p in all_p], name="2026",
        orientation="h", marker_color="#e94560",
        text=[f"{df26.get(p, 0):.1f}%" for p in all_p], textposition="outside",
    ))
    fig.add_vline(x=0, line_color="white")
    fig.update_layout(
        title="State-wide Vote Share: 2021 vs 2026",
        barmode="relative",
        template="plotly_dark",
        height=max(400, len(all_p) * 45),
        xaxis_title="← 2021 | 2026 →",
    )
    return fig


def vote_share_small_multiples(vs: pd.DataFrame, major_parties: list) -> go.Figure:
    """6 small bar charts — vote share by region for 2021 vs 2026."""
    regions = REGION_ORDER
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=regions,
        shared_yaxes=True,
    )
    for i, region in enumerate(regions):
        row, col = divmod(i, 3)
        for year, color in [(2021, "#4a90d9"), (2026, "#e94560")]:
            sub = vs[(vs["year"] == year) & (vs["scope"] == region) & (vs["party"].isin(major_parties))]
            fig.add_trace(
                go.Bar(x=sub["party"], y=sub["vote_share_pct"],
                       name=str(year), marker_color=color,
                       showlegend=(i == 0)),
                row=row + 1, col=col + 1,
            )
    fig.update_layout(
        title="Vote Share by Region (2021 vs 2026)",
        barmode="group",
        template="plotly_dark",
        height=600,
    )
    return fig
