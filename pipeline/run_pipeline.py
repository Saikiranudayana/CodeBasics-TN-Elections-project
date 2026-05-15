"""pipeline/run_pipeline.py — Single entry-point to run the data pipeline."""

import logging
import pathlib
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

BASE_DIR = pathlib.Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
TIMESTAMP_FILE = PROCESSED_DIR / ".pipeline_timestamp"


def main():
    import pandas as pd
    # Import pipeline modules (works whether run as script or module)
    sys.path.insert(0, str(BASE_DIR))
    from pipeline.cleaner import clean_results, validate_cleaned
    from pipeline.preprocessor import (
        build_winners,
        build_vote_share,
        build_seat_counts,
        build_flip_seats,
        build_margin_analysis,
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Read raw CSVs
    logger.info("Reading raw CSVs from %s", RAW_DIR)
    try:
        df21_raw = pd.read_csv(RAW_DIR / "tn_2021_results.csv")
        df26_raw = pd.read_csv(RAW_DIR / "tn_2026_results.csv")
        master = pd.read_csv(RAW_DIR / "constituency_master.csv")
    except FileNotFoundError as e:
        print(
            f"\n[ERROR] Missing raw CSV file: {e}\n"
            f"Please ensure the following files exist in {RAW_DIR}:\n"
            "  - tn_2021_results.csv\n"
            "  - tn_2026_results.csv\n"
            "  - constituency_master.csv\n"
        )
        sys.exit(1)

    # Merge master data (district, region, reserved) into results if missing
    for col in ["region", "reserved", "constituency"]:
        if col not in df21_raw.columns and col in master.columns:
            df21_raw = df21_raw.merge(master[["ac_number", col]], on="ac_number", how="left")
        if col not in df26_raw.columns and col in master.columns:
            df26_raw = df26_raw.merge(master[["ac_number", col]], on="ac_number", how="left")

    # 2. Clean both years
    logger.info("Cleaning 2021 data...")
    df21 = clean_results(df21_raw, 2021)
    logger.info("Cleaning 2026 data...")
    df26 = clean_results(df26_raw, 2026)

    # 3. Validate
    logger.info("Validating cleaned data...")
    validate_cleaned(df21, 2021)
    validate_cleaned(df26, 2026)

    # 4. Build processed tables
    logger.info("Building winners tables...")
    w21 = build_winners(df21)
    w26 = build_winners(df26)

    logger.info("Building vote share tables...")
    vs21 = build_vote_share(df21)
    vs26 = build_vote_share(df26)
    vote_share = pd.concat([vs21, vs26], ignore_index=True)

    logger.info("Building seat counts tables...")
    sc21 = build_seat_counts(w21)
    sc26 = build_seat_counts(w26)
    seat_swing = pd.concat([sc21, sc26], ignore_index=True)

    logger.info("Building flip seats table...")
    flip_seats = build_flip_seats(w21, w26)

    logger.info("Building margin analysis table...")
    margin_analysis = build_margin_analysis(w21, w26)

    # 5. Save to parquet
    outputs = {
        "winners_2021.parquet": w21,
        "winners_2026.parquet": w26,
        "vote_share.parquet": vote_share,
        "seat_swing.parquet": seat_swing,
        "flip_seats.parquet": flip_seats,
        "margin_analysis.parquet": margin_analysis,
    }

    for fname, df in outputs.items():
        path = PROCESSED_DIR / fname
        df.to_parquet(path, index=False)
        logger.info("Saved %s (%d rows)", fname, len(df))

    # Write timestamp
    TIMESTAMP_FILE.write_text(str(time.time()))

    # 6. Print summary table
    print("\n" + "=" * 60)
    print("  TN Election Dashboard — Pipeline Complete")
    print("=" * 60)
    print(f"  {'File':<35} {'Rows':>6}  {'Size':>10}")
    print("-" * 60)
    for fname in outputs:
        path = PROCESSED_DIR / fname
        size_kb = path.stat().st_size / 1024
        rows = len(outputs[fname])
        print(f"  {fname:<35} {rows:>6}  {size_kb:>8.1f}KB")
    print("=" * 60)
    print(f"\n  Processed files saved to: {PROCESSED_DIR}\n")


if __name__ == "__main__":
    main()
