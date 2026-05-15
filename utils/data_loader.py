"""utils/data_loader.py — Cached data loading helpers for the dashboard."""

import pathlib
import pandas as pd
import streamlit as st

from utils.constants import PARTY_COLORS

BASE_DIR = pathlib.Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR = BASE_DIR / "data" / "raw"
TIMESTAMP_FILE = PROCESSED_DIR / ".pipeline_timestamp"


@st.cache_data(ttl=3600)
def load_winners(year: int) -> pd.DataFrame:
    """Load winners_{year}.parquet from data/processed/."""
    return pd.read_parquet(PROCESSED_DIR / f"winners_{year}.parquet")


@st.cache_data(ttl=3600)
def load_vote_share() -> pd.DataFrame:
    """Load vote_share.parquet from data/processed/."""
    return pd.read_parquet(PROCESSED_DIR / "vote_share.parquet")


@st.cache_data(ttl=3600)
def load_seat_swing() -> pd.DataFrame:
    """Load seat_swing.parquet (seat counts) from data/processed/."""
    return pd.read_parquet(PROCESSED_DIR / "seat_swing.parquet")


@st.cache_data(ttl=3600)
def load_flip_seats() -> pd.DataFrame:
    """Load flip_seats.parquet from data/processed/."""
    return pd.read_parquet(PROCESSED_DIR / "flip_seats.parquet")


@st.cache_data(ttl=3600)
def load_margin_analysis() -> pd.DataFrame:
    """Load margin_analysis.parquet from data/processed/."""
    return pd.read_parquet(PROCESSED_DIR / "margin_analysis.parquet")


@st.cache_data(ttl=3600)
def load_raw(year: int) -> pd.DataFrame:
    """Load the raw cleaned CSV for per-candidate analysis."""
    return pd.read_csv(RAW_DIR / f"tn_{year}_results.csv")


def get_party_color(party: str) -> str:
    """Return the hex colour for a party, or a fallback grey."""
    return PARTY_COLORS.get(party, "#CCCCCC")


def get_pipeline_timestamp() -> str:
    """Return a human-readable timestamp of the last pipeline run."""
    if TIMESTAMP_FILE.exists():
        import datetime
        ts = float(TIMESTAMP_FILE.read_text().strip())
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime("%d %b %Y %H:%M")
    return "Never"


def processed_files_exist() -> bool:
    """Check if all required processed parquet files exist."""
    required = [
        "winners_2021.parquet",
        "winners_2026.parquet",
        "vote_share.parquet",
        "seat_swing.parquet",
        "flip_seats.parquet",
        "margin_analysis.parquet",
    ]
    return all((PROCESSED_DIR / f).exists() for f in required)
