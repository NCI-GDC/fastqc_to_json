#!/usr/bin/env python

import json
import os
import sqlite3
import sys
from typing import Any, Dict, List, Tuple

import click

NORMAL_COLS = ("job_uuid", "fastq", "Measure", "Value")
BROKEN_COLS = ("('job_uuid',)", "('fastq',)", "('Measure',)", "('Value',)")


def detect_columns(cursor: sqlite3.Cursor) -> Tuple[str, str, str, str]:
    cursor.execute("PRAGMA table_info(fastqc_data_Basic_Statistics);")
    cols = {row[1] for row in cursor.fetchall()}

    if all(c in cols for c in NORMAL_COLS):
        return NORMAL_COLS

    if all(c in cols for c in BROKEN_COLS):
        return BROKEN_COLS

    sys.stderr.write(
        "ERROR: fastqc_data_Basic_Statistics does not contain usable columns.\n"
        f"Found columns: {sorted(cols)}\n"
    )
    sys.exit(1)


def db_to_json(result: List[Tuple[Any, Any, Any, Any]]) -> Dict[str, Any]:
    data: Dict[str, Any] = dict()

    for line in result:
        fastq = line[1]
        key = line[2]
        value = line[3]

        if key == "Filename":
            filename = value
            data[filename] = dict()

        elif key == "File type":
            data[filename][key] = value

        elif key == "Encoding":
            data[filename][key] = value

        elif key == "Total Sequences":
            data[filename][key] = int(value)

        elif key == "Sequences flagged as poor quality":
            data[filename][key] = int(value)

        elif key == "Sequence length":
            if "-" in value:
                value_split = value.split("-")
                value_int = [int(x) for x in value_split]
                value = max(value_int)

            data[filename][key] = int(value)

        elif key == "%GC":
            data[filename][key] = int(value)

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp)

    return data


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help=("fastqc Basic Statistics to json"),
)
@click.option(
    "--sqlite_path",
    required=True,
    type=click.Path(exists=True),
    help="path of sqlite file",
)
def main(sqlite_path: str) -> int:
    # if no data, then output zero byte json file
    sqlite_size = os.path.getsize(sqlite_path)

    if sqlite_size == 0:
        open("fastqc.json", "w").close()
        return 0

    # if data, then output populated json
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    job_col, fastq_col, measure_col, value_col = detect_columns(cursor)

    query = f"""
        SELECT
            "{job_col}",
            "{fastq_col}",
            "{measure_col}",
            "{value_col}"
        FROM fastqc_data_Basic_Statistics;
    """

    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except sqlite3.DatabaseError as e:
        sys.stderr.write(f"ERROR: SQLite query failed: {e}\n")
        conn.close()
        return 1

    conn.close()

    db_to_json(result)

    return 0


if __name__ == "__main__":
    main()
