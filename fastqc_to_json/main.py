#!/usr/bin/env python

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


def db_to_json(sqlite_path: str) -> Dict[str, Any]:
    data: Dict[str, Any] = dict()

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

    cursor.execute(query)
    rows: List[Tuple[Any, Any, Any, Any]] = cursor.fetchall()

    conn.close()

    for job_uuid, fastq, key, value in rows:
        if fastq not in data:
            data[fastq] = dict()

        if key == "Filename":
            continue

        elif key == "File type":
            data[fastq][key] = value

        elif key == "Encoding":
            data[fastq][key] = value

        elif key == "Total Sequences":
            data[fastq][key] = int(value)

        elif key == "Sequences flagged as poor quality":
            data[fastq][key] = int(value)

        elif key == "Sequence length":
            if "-" in value:
                value_split = value.split("-")
                value_int = [int(x) for x in value_split]
                value = max(value_int)

            data[fastq][key] = int(value)

        elif key == "%GC":
            data[fastq][key] = int(value)

    with open(OUTPUT_JSON, "w") as fp:
        json.dump(data, fp)

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
