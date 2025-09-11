"""
Consumer Data Exporter
======================

Builds consumer-ready CSVs from QC outputs with the following rules:
- Include data from the live logger only (ignore backup logger data)
- Remove values that failed QC (keep rows; blank out failing values)
- Exclude all indicator (ind_*) columns from outputs
- Produce one CSV per buoy per year into Consumers/Data/

Usage:
  python consumer_export.py
"""

import os
import pandas as pd
from datetime import datetime


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
QC_DATA_DIR = os.path.join(PROJECT_ROOT, "QC", "Data")
BUOY_DATA_DIR = os.path.join(PROJECT_ROOT, "Buoy Data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "Consumers", "Data")


def load_logger_information(logger_csv_path: str) -> dict:
    """Load live logger intervals per station from imdbon_log_of_loggers.csv

    Returns: dict[station] -> list of {logger_id, start_time, end_time, is_live}
    """
    logger_info: dict[str, list[dict]] = {}

    if not os.path.exists(logger_csv_path):
        print(f"Warning: Logger information file not found at {logger_csv_path}")
        return logger_info

    df = pd.read_csv(logger_csv_path)

    # Normalize and parse
    def parse_dt(value: str):
        if pd.isna(value):
            return None
        for fmt in ("%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(str(value), fmt)
            except Exception:
                continue
        # Fallback to pandas parser
        try:
            return pd.to_datetime(value, errors="coerce").to_pydatetime()
        except Exception:
            return None

    for _, row in df.iterrows():
        station = str(row.get("Buoy", "")).strip()
        logger_id = str(row.get("Loggerid", "")).strip()
        if not station or not logger_id:
            continue

        start_time = parse_dt(row.get("Start"))
        end_time = parse_dt(row.get("End")) if pd.notna(row.get("End")) else None
        is_live = bool(row.get("Live", 0))

        if station not in logger_info:
            logger_info[station] = []
        logger_info[station].append(
            {
                "logger_id": logger_id,
                "start_time": start_time,
                "end_time": end_time,
                "is_live": is_live,
            }
        )

    # Sort by start time
    for station in logger_info:
        logger_info[station].sort(key=lambda x: (x["start_time"] or datetime.min))

    return logger_info


def choose_live_logger_for_period(logger_info: dict, station: str, start_time: pd.Timestamp, end_time: pd.Timestamp):
    """Pick the live logger covering the majority of [start_time, end_time]."""
    if station not in logger_info:
        return None

    period_start = pd.to_datetime(start_time)
    period_end = pd.to_datetime(end_time)

    best_logger = None
    best_coverage = 0.0

    for entry in logger_info[station]:
        if not entry.get("is_live", False):
            continue

        logger_start = entry["start_time"] or period_start.to_pydatetime()
        logger_end = entry["end_time"] or period_end.to_pydatetime()

        overlap_start = max(period_start.to_pydatetime(), logger_start)
        overlap_end = min(period_end.to_pydatetime(), logger_end)

        if overlap_start < overlap_end:
            overlap_seconds = (overlap_end - overlap_start).total_seconds()
            period_seconds = max((period_end - period_start).total_seconds(), 1.0)
            coverage = overlap_seconds / period_seconds
            if coverage > best_coverage:
                best_coverage = coverage
                best_logger = entry

    return best_logger if best_coverage > 0 else None


def numeric_logger_token(logger_id: str) -> str:
    """Extract a stable token used in data 'loggerid' for filtering (e.g., '8704' from '8704_CR6')."""
    if not logger_id:
        return ""
    token = str(logger_id).split("_")[0].strip()
    return token


def apply_consumer_filtering(df: pd.DataFrame) -> pd.DataFrame:
    """Blank out values that failed QC, then drop indicator columns.

    Passing indicators: 1 (OK), 5 (adjusted OK), 6 (Datawell Hmax OK)
    Everything else (0, 4, 9, or missing) is treated as not acceptable for consumers.
    """
    acceptable_inds = {1, 5, 6}

    # Identify indicator columns
    ind_cols = [c for c in df.columns if c.startswith("ind_")]

    # For each indicator column, blank out the paired value when indicator is not acceptable
    for ind_col in ind_cols:
        base_param = ind_col[len("ind_"):]
        if base_param in df.columns:
            mask_fail = ~df[ind_col].isin(acceptable_inds)
            # Preserve missing as missing; blank only those explicitly not accepted
            df.loc[mask_fail, base_param] = pd.NA

    # Drop all indicator columns from output
    df = df.drop(columns=ind_cols, errors="ignore")

    return df


def export_consumers_data():
    print("=== CONSUMER EXPORT START ===")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load logger metadata
    logger_csv = os.path.join(BUOY_DATA_DIR, "imdbon_log_of_loggers.csv")
    logger_info = load_logger_information(logger_csv)

    # Discover QC Data files
    qc_files = [f for f in os.listdir(QC_DATA_DIR) if f.endswith("_qcd.csv") and f.startswith("buoy_")]
    if not qc_files:
        print("No QC data found to export.")
        return 0

    total_written = 0

    for file_name in sorted(qc_files):
        # Expect format: buoy_{station}_{year}_qcd.csv
        # Example: buoy_62091_2024_qcd.csv
        try:
            parts = file_name.replace(".csv", "").split("_")
            station = parts[1]
            year = parts[2]
        except Exception:
            print(f"Skipping unrecognized file name: {file_name}")
            continue

        file_path = os.path.join(QC_DATA_DIR, file_name)
        print(f"Processing {file_name} ...")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"  Failed to read: {e}")
            continue

        # Ensure time is datetime for range and sorting
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
            df = df.sort_values("time").reset_index(drop=True)

        # Filter to live logger only when metadata available
        if logger_info and "loggerid" in df.columns and len(df) > 0:
            start_time = df["time"].min() if "time" in df.columns else None
            end_time = df["time"].max() if "time" in df.columns else None

            live_logger = None
            if start_time is not None and end_time is not None:
                live_logger = choose_live_logger_for_period(logger_info, station, start_time, end_time)

            if live_logger:
                token = numeric_logger_token(live_logger["logger_id"])
                if token:
                    before = len(df)
                    df = df[df["loggerid"].astype(str).str.contains(token, na=False)].copy()
                    after = len(df)
                    print(f"  Live logger: {live_logger['logger_id']} -> filtered {before} → {after} rows")
                else:
                    print("  Warning: Could not derive numeric token for live logger; skipping logger filter")
            else:
                print("  Warning: Live logger not identified for this period; skipping logger filter")
        else:
            print("  Logger metadata unavailable or no loggerid column; skipping logger filter")

        # Apply consumer filtering (blank failing values; drop indicators)
        df = apply_consumer_filtering(df)

        # Drop logger identifier from consumer outputs
        drop_logger_cols = [c for c in df.columns if str(c).strip().lower() == "loggerid"]
        if drop_logger_cols:
            df = df.drop(columns=drop_logger_cols, errors="ignore")

        # Write output file
        out_name = f"buoy_{station}_{year}_consumer.csv"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        df.to_csv(out_path, index=False)
        print(f"  Wrote {out_name} with {len(df):,} rows and {len(df.columns)} columns")
        total_written += 1

    print(f"=== CONSUMER EXPORT COMPLETE: {total_written} file(s) written ===")
    return total_written


if __name__ == "__main__":
    export_consumers_data()


