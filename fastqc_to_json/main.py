#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List

OUTPUT_JSON = "fastqc.json"


def run_sqlite_query(sqlite_path: str) -> List[str]:
    """
    Run a SQLite query to get the broken fastqc_data_Basic_Statistics schema.
    Returns raw sqlite3 output lines.
    """
    query = """
    SELECT
        "('job_uuid',)",
        "('fastq',)",
        "('Measure',)",
        "('Value',)"
    FROM fastqc_data_Basic_Statistics;
    """

    try:
        output = subprocess.check_output(
            ["sqlite3", sqlite_path, query], stderr=subprocess.STDOUT
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"ERROR: sqlite3 failed:\n{e.output.decode()}\n")
        sys.exit(1)

    # Only non-empty lines
    return [line for line in output.splitlines() if line.strip()]


def coerce_value(raw: str) -> Any:
    """Convert SQLite text values to int or float if possible, otherwise keep string."""
    try:
        if "." in raw:
            f = float(raw)
            return int(f) if f.is_integer() else f
        return int(raw)
    except ValueError:
        return raw


def db_to_json(rows: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Convert SQLite output rows into fastqc.json
    Rows are expected in the broken schema with:
    0-4 ignored, 5=job_uuid, 6=fastq, 7=Measure, 8=Value
    """
    data: Dict[str, Dict[str, Any]] = {}

    for line in rows:
        parts = line.strip().split("|")
        if len(parts) < 9:
            continue

        fastq = parts[6]
        measure = parts[7]
        raw_value = parts[8]

        if fastq not in data:
            data[fastq] = {}

        value = coerce_value(raw_value)
        data[fastq][measure] = value

    # Always produce a JSON file, even if empty
    with open(OUTPUT_JSON, "w") as fp:
        json.dump(data, fp, indent=2)

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
    sqlite_path = args.sqlite_path

    # Check the DB exists
    if not os.path.exists(sqlite_path):
        sys.stderr.write(f"ERROR: SQLite DB not found: {sqlite_path}\n")
        return 1

    # Empty DB → produce empty JSON explicitly
    if os.path.getsize(sqlite_path) == 0:
        with open(OUTPUT_JSON, "w") as fp:
            fp.write("{}")
        return 0

    # Run query and convert to JSON
    rows = run_sqlite_query(sqlite_path)
    data = db_to_json(rows)

    if not data:
        sys.stderr.write(
            "WARNING: Database contained no usable rows. JSON produced but may be empty.\n"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
