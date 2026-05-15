"""components/drastic_detector.py — Detect statistically significant changes between 2021 and 2026."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DrasticAlert:
    alert_type: str        # "SEAT_SWING" | "VOTE_SHARE_CRASH" | "NEW_FORCE" | "MARGIN_COLLAPSE" | "REGION_FLIP"
    severity: str          # "HIGH" | "MEDIUM" | "LOW"
    title: str             # Short headline (max 10 words)
    body: str              # 2–3 sentence description with exact numbers
    entity: str            # party name, region name, or constituency name
    metric_before: float   # value in 2021
    metric_after: float    # value in 2026
    change: float          # metric_after - metric_before
    search_query: str      # pre-built Tavily query


_SEVERITY_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def detect_seat_swings(w21, w26) -> List[DrasticAlert]:
    """Detect large seat count changes between elections."""
    alerts = []

    seats21 = w21.groupby("winner_party").size()
    seats26 = w26.groupby("winner_party").size()
    all_parties = set(seats21.index) | set(seats26.index)

    for party in all_parties:
        s21 = int(seats21.get(party, 0))
        s26 = int(seats26.get(party, 0))
        seat_change = s26 - s21
        pct_change = seat_change / max(s21, 1) * 100

        if abs(pct_change) >= 50 and abs(seat_change) >= 10:
            severity = "HIGH"
        elif abs(pct_change) >= 30 and abs(seat_change) >= 5:
            severity = "MEDIUM"
        else:
            continue

        direction = "collapsed" if seat_change < 0 else "surged"
        sign = "−" if seat_change < 0 else "+"
        title = f"{party} seats {direction}: {s21} → {s26} ({sign}{abs(int(pct_change))}%)"
        body = (
            f"{party} won {s26} seats in 2026, compared to {s21} seats in 2021 — "
            f"a change of {seat_change:+d} seats ({pct_change:+.1f}%). "
            f"This represents a {'major loss' if seat_change < 0 else 'major gain'} for the party."
        )
        query = f"{party} 2026 Tamil Nadu election seat swing results news"
        alerts.append(DrasticAlert(
            alert_type="SEAT_SWING",
            severity=severity,
            title=title,
            body=body,
            entity=party,
            metric_before=float(s21),
            metric_after=float(s26),
            change=float(seat_change),
            search_query=query,
        ))

    return alerts


def detect_vote_share_crashes(vs) -> List[DrasticAlert]:
    """Detect major vote share changes between elections."""
    alerts = []

    state21 = vs[(vs["year"] == 2021) & (vs["scope"] == "state")].set_index("party")["vote_share_pct"]
    state26 = vs[(vs["year"] == 2026) & (vs["scope"] == "state")].set_index("party")["vote_share_pct"]
    all_parties = set(state21.index) | set(state26.index)

    for party in all_parties:
        vs21 = float(state21.get(party, 0.0))
        vs26 = float(state26.get(party, 0.0))
        change_pp = vs26 - vs21

        # New entrant with significant share
        if vs21 == 0 and vs26 >= 3.0:
            title = f"{party}: new force — {vs26:.1f}% vote share in 2026"
            body = (
                f"{party} is a new party that did not exist in 2021 but captured {vs26:.1f}% "
                f"of the state-wide vote in 2026. This marks a significant new political force in Tamil Nadu."
            )
            query = f"{party} 2026 Tamil Nadu election new party vote share news"
            alerts.append(DrasticAlert(
                alert_type="NEW_FORCE",
                severity="HIGH",
                title=title,
                body=body,
                entity=party,
                metric_before=0.0,
                metric_after=vs26,
                change=vs26,
                search_query=query,
            ))
            continue

        if abs(change_pp) >= 8:
            severity = "HIGH"
        elif abs(change_pp) >= 4:
            severity = "MEDIUM"
        else:
            continue

        direction = "crashed" if change_pp < 0 else "surged"
        title = f"{party} vote share {direction}: {vs21:.1f}% → {vs26:.1f}%"
        body = (
            f"{party}'s state-wide vote share moved from {vs21:.1f}% in 2021 to {vs26:.1f}% in 2026 "
            f"({change_pp:+.1f} percentage points). "
            f"This is a {'significant decline' if change_pp < 0 else 'significant increase'} in popular support."
        )
        query = f"{party} 2026 Tamil Nadu election vote share {direction} results news"
        alerts.append(DrasticAlert(
            alert_type="VOTE_SHARE_CRASH",
            severity=severity,
            title=title,
            body=body,
            entity=party,
            metric_before=vs21,
            metric_after=vs26,
            change=change_pp,
            search_query=query,
        ))

    return alerts


def detect_region_flips(w21, w26) -> List[DrasticAlert]:
    """Detect regions where dominant party changed between elections."""
    alerts = []

    for region in w21["region"].dropna().unique():
        seats21 = w21[w21["region"] == region]["winner_party"].value_counts()
        seats26 = w26[w26["region"] == region]["winner_party"].value_counts()
        dominant21 = seats21.idxmax() if not seats21.empty else None
        dominant26 = seats26.idxmax() if not seats26.empty else None

        if dominant21 and dominant26 and dominant21 != dominant26:
            s21 = int(seats21[dominant21])
            s26 = int(seats26[dominant26])
            title = f"{region} flipped: {dominant21} → {dominant26}"
            body = (
                f"In {region}, {dominant21} was the dominant party in 2021 with {s21} seats. "
                f"In 2026, {dominant26} became the dominant party with {s26} seats. "
                f"This represents a significant regional political shift."
            )
            query = f"{region} region 2026 Tamil Nadu election results political shift news"
            alerts.append(DrasticAlert(
                alert_type="REGION_FLIP",
                severity="HIGH",
                title=title,
                body=body,
                entity=region,
                metric_before=float(s21),
                metric_after=float(s26),
                change=float(s26 - s21),
                search_query=query,
            ))

    return alerts


def detect_margin_collapse(margin_df) -> List[DrasticAlert]:
    """Detect constituencies with dramatic margin changes or narrow flips."""
    alerts = []

    # Large margin percentage drop
    collapsed = margin_df[margin_df["margin_pct_change"] <= -15].copy()
    collapsed = collapsed.reindex(collapsed["margin_pct_change"].abs().sort_values(ascending=False).index)
    for _, row in collapsed.head(10).iterrows():
        change = float(row["margin_pct_change"])
        title = f"{row['constituency']}: margin collapsed {row['margin_pct_2021']:.1f}% → {row['margin_pct_2026']:.1f}%"
        body = (
            f"In {row['constituency']}, the winning margin dropped from {row['margin_pct_2021']:.1f}% in 2021 "
            f"to {row['margin_pct_2026']:.1f}% in 2026 ({change:+.1f} pp). "
            f"The 2026 winner was {row['winner_party_2026']}."
        )
        query = f"{row['constituency']} constituency 2026 Tamil Nadu election margin collapse results news"
        alerts.append(DrasticAlert(
            alert_type="MARGIN_COLLAPSE",
            severity="MEDIUM",
            title=title,
            body=body,
            entity=row["constituency"],
            metric_before=float(row["margin_pct_2021"]),
            metric_after=float(row["margin_pct_2026"]),
            change=change,
            search_query=query,
        ))

    # Narrow flip seats (margin < 2%)
    flipped_narrow = margin_df[
        (margin_df["winner_party_2021"] != margin_df["winner_party_2026"]) &
        (margin_df["margin_pct_2026"] < 2.0)
    ]
    for _, row in flipped_narrow.head(5).iterrows():
        title = f"{row['constituency']}: narrow flip with {row['margin_pct_2026']:.1f}% margin"
        body = (
            f"{row['constituency']} flipped from {row['winner_party_2021']} (2021) to "
            f"{row['winner_party_2026']} (2026) with a razor-thin margin of {row['margin_pct_2026']:.1f}% "
            f"({int(row['margin_2026'])} votes)."
        )
        query = f"{row['constituency']} constituency 2026 Tamil Nadu election narrow margin flip news"
        alerts.append(DrasticAlert(
            alert_type="MARGIN_COLLAPSE",
            severity="LOW",
            title=title,
            body=body,
            entity=row["constituency"],
            metric_before=float(row["margin_pct_2021"]),
            metric_after=float(row["margin_pct_2026"]),
            change=float(row["margin_pct_2026"] - row["margin_pct_2021"]),
            search_query=query,
        ))

    return alerts


def detect_all_drastic_changes(w21, w26, vs, flip_df) -> List[DrasticAlert]:
    """Run all detectors and return deduplicated, sorted alerts."""
    all_alerts = []
    all_alerts.extend(detect_seat_swings(w21, w26))
    all_alerts.extend(detect_vote_share_crashes(vs))
    all_alerts.extend(detect_region_flips(w21, w26))

    # Build margin df on-the-fly if needed
    try:
        from pipeline.preprocessor import build_margin_analysis
        margin_df = build_margin_analysis(w21, w26)
        all_alerts.extend(detect_margin_collapse(margin_df))
    except Exception:
        pass

    # Deduplicate by (entity, alert_type)
    seen = set()
    unique_alerts = []
    for alert in all_alerts:
        key = (alert.entity, alert.alert_type)
        if key not in seen:
            seen.add(key)
            unique_alerts.append(alert)

    # Sort: HIGH first, then MEDIUM, then LOW
    unique_alerts.sort(key=lambda a: _SEVERITY_ORDER.get(a.severity, 99))
    return unique_alerts
