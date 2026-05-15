"""pipeline/preprocessor.py — Build processed tables from cleaned data."""

import pandas as pd


def build_winners(df: pd.DataFrame) -> pd.DataFrame:
    """Find the winning candidate in each constituency."""
    results = []
    for ac_number, group in df.groupby("ac_number"):
        total_votes = group["votes"].sum()
        valid_votes = group.loc[group["party"] != "NOTA", "votes"].sum()
        sorted_group = group.sort_values("votes", ascending=False)
        winner = sorted_group.iloc[0]
        second_votes = sorted_group.iloc[1]["votes"] if len(sorted_group) > 1 else 0
        margin = int(winner["votes"] - second_votes)
        margin_pct = margin / total_votes * 100 if total_votes > 0 else 0.0
        winner_vote_share = winner["votes"] / total_votes * 100 if total_votes > 0 else 0.0
        num_candidates = len(group)

        results.append({
            "ac_number": int(ac_number),
            "constituency": winner.get("constituency", ""),
            "region": winner.get("region", ""),
            "reserved": winner.get("reserved", "GEN"),
            "year": int(winner["year"]),
            "winner_candidate": winner.get("candidate", ""),
            "winner_party": winner["party"],
            "winner_votes": int(winner["votes"]),
            "total_votes": int(total_votes),
            "valid_votes": int(valid_votes),
            "winner_vote_share": round(winner_vote_share, 4),
            "margin": margin,
            "margin_pct": round(margin_pct, 4),
            "num_candidates": num_candidates,
        })

    return pd.DataFrame(results)


def build_vote_share(df: pd.DataFrame) -> pd.DataFrame:
    """Compute state-wide and per-region vote share for each party."""
    year = int(df["year"].iloc[0])
    rows = []

    # State-wide
    grand_total = df["votes"].sum()
    state_party = df.groupby("party")["votes"].sum().reset_index()
    for _, row in state_party.iterrows():
        rows.append({
            "year": year,
            "scope": "state",
            "party": row["party"],
            "votes": int(row["votes"]),
            "vote_share_pct": round(row["votes"] / grand_total * 100, 4) if grand_total > 0 else 0.0,
        })

    # Per-region
    if "region" in df.columns:
        for region, rgroup in df.groupby("region"):
            region_total = rgroup["votes"].sum()
            region_party = rgroup.groupby("party")["votes"].sum().reset_index()
            for _, row in region_party.iterrows():
                rows.append({
                    "year": year,
                    "scope": str(region),
                    "party": row["party"],
                    "votes": int(row["votes"]),
                    "vote_share_pct": round(row["votes"] / region_total * 100, 4) if region_total > 0 else 0.0,
                })

    return pd.DataFrame(rows)


def build_seat_counts(winners: pd.DataFrame) -> pd.DataFrame:
    """Count seats won per party across different groupings."""
    year = int(winners["year"].iloc[0])
    rows = []

    # State-wide
    state_counts = winners.groupby("winner_party").size().reset_index(name="seats_won")
    for _, row in state_counts.iterrows():
        rows.append({
            "year": year,
            "grouping": "state",
            "group_value": "state",
            "party": row["winner_party"],
            "seats_won": int(row["seats_won"]),
        })

    # Per region
    if "region" in winners.columns:
        region_counts = winners.groupby(["region", "winner_party"]).size().reset_index(name="seats_won")
        for _, row in region_counts.iterrows():
            rows.append({
                "year": year,
                "grouping": "region",
                "group_value": str(row["region"]),
                "party": row["winner_party"],
                "seats_won": int(row["seats_won"]),
            })

    # Per reserved
    if "reserved" in winners.columns:
        reserved_counts = winners.groupby(["reserved", "winner_party"]).size().reset_index(name="seats_won")
        for _, row in reserved_counts.iterrows():
            rows.append({
                "year": year,
                "grouping": "reserved",
                "group_value": str(row["reserved"]),
                "party": row["winner_party"],
                "seats_won": int(row["seats_won"]),
            })

    return pd.DataFrame(rows)


def build_flip_seats(w21: pd.DataFrame, w26: pd.DataFrame) -> pd.DataFrame:
    """Identify constituencies that flipped party between 2021 and 2026."""
    merged = w21.merge(
        w26,
        on="ac_number",
        suffixes=("_2021", "_2026"),
    )
    merged["is_flip"] = merged["winner_party_2021"] != merged["winner_party_2026"]

    cols = [
        "ac_number",
        "constituency_2026",
        "region_2026",
        "reserved_2026",
        "winner_party_2021",
        "winner_party_2026",
        "is_flip",
        "margin_2021",
        "margin_2026",
        "winner_votes_2021",
        "winner_votes_2026",
    ]
    out = merged[cols].copy()
    out = out.rename(columns={
        "constituency_2026": "constituency",
        "region_2026": "region",
        "reserved_2026": "reserved",
    })
    return out


def build_margin_analysis(w21: pd.DataFrame, w26: pd.DataFrame) -> pd.DataFrame:
    """Join winners and compute margin change metrics."""
    merged = w21.merge(
        w26,
        on="ac_number",
        suffixes=("_2021", "_2026"),
    )
    merged["margin_change"] = merged["margin_2026"] - merged["margin_2021"]
    merged["margin_pct_change"] = merged["margin_pct_2026"] - merged["margin_pct_2021"]

    def categorise(row):
        vs = row["winner_vote_share_2026"]
        if vs >= 50:
            return "Landslide"
        elif vs >= 40:
            return "Comfortable"
        else:
            return "Narrow"

    merged["category_2026"] = merged.apply(categorise, axis=1)

    keep_cols = [
        "ac_number",
        "constituency_2026",
        "region_2026",
        "reserved_2026",
        "winner_party_2021",
        "winner_party_2026",
        "winner_votes_2021",
        "winner_votes_2026",
        "winner_vote_share_2021",
        "winner_vote_share_2026",
        "margin_2021",
        "margin_2026",
        "margin_pct_2021",
        "margin_pct_2026",
        "margin_change",
        "margin_pct_change",
        "category_2026",
    ]
    out = merged[keep_cols].copy()
    out = out.rename(columns={
        "constituency_2026": "constituency",
        "region_2026": "region",
        "reserved_2026": "reserved",
    })
    return out
