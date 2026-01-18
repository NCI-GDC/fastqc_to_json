#!/usr/bin/env python3

import argparse
import json
import os
import sqlite3
import sys
from typing import Any, Dict

OUTPUT_JSON = "fastqc.json"


def db_to_json(sqlite_path: str) -> Dict[str, Dict[str, Any]]:
    """Read fastqc_data_Basic_Statistics table and convert to JSON."""

    if not os.path.exists(sqlite_path):
        sys.stderr.write(f"ERROR: SQLite DB not found: {sqlite_path}\n")
        sys.exit(1)

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT job_uuid, fastq, Measure, Value
            FROM fastqc_data_Basic_Statistics;
            """
        )
        rows = cursor.fetchall()
    except sqlite3.DatabaseError as e:
        sys.stderr.write(f"ERROR: SQLite query failed: {e}\n")
        conn.close()
        sys.exit(1)
    conn.close()

    data: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if len(row) != 4:
            continue
        _, fastq, measure, raw_value = row
        if fastq is None or measure is None or raw_value is None:
            continue

        # Convert numeric values
        try:
            if "." in str(raw_value):
                f = float(raw_value)
                value: Any = int(f) if f.is_integer() else f
            else:
                value = int(raw_value)
        except (ValueError, TypeError):
            value = raw_value

        if fastq not in data:
            data[fastq] = {}

        data[fastq][measure] = value

    # Always write JSON
    with open(OUTPUT_JSON, "w") as fp:
        json.dump(data, fp, indent=2)

    if not data:
        sys.stderr.write(
            "WARNING: Database contained no usable rows. JSON produced but may be empty.\n"
        )

    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert fastqc Basic Statistics table to JSON"
    )
    parser.add_argument(
        "--sqlite_path",
        required=True,
        help="Path to the SQLite database file containing fastqc_data_Basic_Statistics",
    )
    args = parser.parse_args()

    db_to_json(args.sqlite_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
