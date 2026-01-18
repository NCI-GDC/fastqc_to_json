#!/usr/bin/env python3

import argparse
import json
import os
import sqlite3
import sys
from typing import Any, Dict, List, Tuple

OUTPUT_JSON = "fastqc.json"


NORMAL_COLS = ("job_uuid", "fastq", "Measure", "Value")
BROKEN_COLS = ("('job_uuid',)", "('fastq',)", "('Measure',)", "('Value',)")


def _detect_columns(cursor: sqlite3.Cursor) -> Tuple[str, str, str, str]:
    cursor.execute("PRAGMA table_info(fastqc_data_Basic_Statistics);")
    cols = {row[1] for row in cursor.fetchall()}

    if all(c in cols for c in BROKEN_COLS):
        return BROKEN_COLS

    if all(c in cols for c in NORMAL_COLS):
        return NORMAL_COLS

    sys.stderr.write(
        "ERROR: fastqc_data_Basic_Statistics does not contain usable columns.\n"
        f"Found columns: {sorted(cols)}\n"
    )
    sys.exit(1)


def _coerce_value(raw: Any) -> Any:
    if raw is None:
        return None
    try:
        if isinstance(raw, str) and "." in raw:
            f = float(raw)
            return int(f) if f.is_integer() else f
        return int(raw)
    except (ValueError, TypeError):
        return raw


def db_to_json(sqlite_path: str) -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(sqlite_path):
        sys.stderr.write(f"ERROR: SQLite DB not found: {sqlite_path}\n")
        sys.exit(1)

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    job_col, fastq_col, measure_col, value_col = _detect_columns(cursor)

    query = f"""
        SELECT
            "{job_col}",
            "{fastq_col}",
            "{measure_col}",
            "{value_col}"
        FROM fastqc_data_Basic_Statistics
    """

    try:
        cursor.execute(query)
        rows: List[Tuple[Any, Any, Any, Any]] = cursor.fetchall()
    except sqlite3.DatabaseError as e:
        sys.stderr.write(f"ERROR: SQLite query failed: {e}\n")
        conn.close()
        sys.exit(1)

    conn.close()

    data: Dict[str, Dict[str, Any]] = {}

    for job_uuid, fastq, measure, raw_value in rows:
        if not fastq or not measure:
            continue

        value = _coerce_value(raw_value)

        data.setdefault(fastq, {})[measure] = value

    # Always write JSON for CWL
    with open(OUTPUT_JSON, "w") as fp:
        json.dump(data, fp, indent=2)

    if not data:
        sys.stderr.write(
            "ERROR: Database rows found but JSON is empty.\n"
            "This indicates a schema or ingestion error upstream.\n"
        )
        sys.exit(1)

    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert fastqc Basic Statistics table to JSON"
    )
    parser.add_argument(
        "--sqlite_path",
        required=True,
        help="Path to SQLite DB containing fastqc_data_Basic_Statistics",
    )
    args = parser.parse_args()

    db_to_json(args.sqlite_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
