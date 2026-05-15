"""pipeline/cleaner.py — Data cleaning for TN election CSVs."""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def clean_results(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Clean a raw election results dataframe.

    Steps (in order):
    1. Strip whitespace from string columns.
    2. Standardise NOTA party name.
    3. Drop invalid vote rows (except NOTA).
    4. Ensure ac_number is int64.
    5. Ensure votes is int64.
    6. Add year column.
    7. Normalise reserved column.
    8. Normalise region column.
    9. Warn on low-vote constituencies.
    """
    df = df.copy()

    # 1. Strip whitespace from all string columns
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # 2. Standardise NOTA
    nota_variants = [
        "none of the above", "nota", "n.o.t.a", "none of above"
    ]
    mask_nota = df["party"].str.lower().isin(nota_variants)
    df.loc[mask_nota, "party"] = "NOTA"

    # 3. Drop rows where votes is NaN or <= 0, UNLESS party is NOTA
    invalid_mask = (df["votes"].isna() | (df["votes"] <= 0)) & (df["party"] != "NOTA")
    if invalid_mask.any():
        logger.warning("Dropping %d rows with invalid votes (year=%d)", invalid_mask.sum(), year)
    df = df[~invalid_mask].copy()

    # 4. Ensure ac_number is int64
    df["ac_number"] = pd.to_numeric(df["ac_number"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["ac_number"])
    df["ac_number"] = df["ac_number"].astype("int64")

    # 5. Ensure votes is int64 (NOTA rows with 0 are kept, fill NaN with 0)
    df["votes"] = df["votes"].fillna(0)
    df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype("int64")

    # 6. Add year column
    df["year"] = year

    # 7. Normalise reserved column
    reserved_map = {
        "general": "GEN",
        "gen": "GEN",
        "sc": "SC",
        "st": "ST",
    }
    if "reserved" in df.columns:
        df["reserved"] = df["reserved"].str.strip().str.lower().map(
            lambda x: reserved_map.get(x, x.upper() if isinstance(x, str) else x)
        )

    # 8. Normalise region column
    if "region" in df.columns:
        df["region"] = df["region"].str.strip().str.title()

    # 9. Warn on suspicious constituencies (total votes < 100)
    if "ac_number" in df.columns:
        constituency_totals = df.groupby("ac_number")["votes"].sum()
        suspicious = constituency_totals[constituency_totals < 100].index.tolist()
        for ac in suspicious:
            name = df.loc[df["ac_number"] == ac, "constituency"].iloc[0] if "constituency" in df.columns else str(ac)
            logger.warning(
                "Constituency ac_number=%d (%s) has very low total votes (%d) — possible data issue.",
                ac, name, constituency_totals[ac]
            )

    return df


def validate_cleaned(df: pd.DataFrame, year: int) -> None:
    """Validate the cleaned dataframe and log a summary."""
    # Check 234 unique ac_numbers
    unique_acs = df["ac_number"].nunique()
    if unique_acs != 234:
        raise ValueError(
            f"Expected 234 unique ac_numbers in year {year}, got {unique_acs}."
        )

    # No negative vote counts
    neg_votes = (df["votes"] < 0).sum()
    if neg_votes > 0:
        raise ValueError(f"Found {neg_votes} rows with negative votes in year {year}.")

    # No NaN in party column
    nan_party = df["party"].isna().sum()
    if nan_party > 0:
        raise ValueError(f"Found {nan_party} NaN values in party column for year {year}.")

    # Log summary
    total_rows = len(df)
    total_constituencies = df["ac_number"].nunique()
    unique_parties = df["party"].nunique()
    total_votes = df["votes"].sum()
    logger.info(
        "Year %d — rows=%d, constituencies=%d, unique_parties=%d, total_votes=%d",
        year, total_rows, total_constituencies, unique_parties, total_votes
    )
