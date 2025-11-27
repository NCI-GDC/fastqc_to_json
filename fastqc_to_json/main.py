#!/usr/bin/env python3

import json
import os
import subprocess
from typing import Any, Dict, List

import click


def db_to_json(rows: List[str]) -> None:
    """
    Convert SQLite output rows into fastqc.json for the NEW database structure.

    Row format from new fastqc_data_Basic_Statistics:
        job_uuid|fastq|Measure|Value
    """

    data: Dict[str, Dict[str, Any]] = {}

    for line in rows:
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")
        if len(parts) != 4:
            continue  # Not a valid row

        job_uuid, fastq, measure, raw_value = parts

        if fastq not in data:
            data[fastq] = {}

        # Attempt numeric conversion
        value: Any
        try:
            if "." in raw_value:
                f = float(raw_value)
                value = int(f) if f.is_integer() else f
            else:
                value = int(raw_value)
        except ValueError:
            value = raw_value

        data[fastq][measure] = value

    # Write JSON output
    with open("fastqc.json", "w") as fp:
        json.dump(data, fp, indent=2)


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="Convert fastqc_data_Basic_Statistics table into JSON (NEW DB STRUCTURE).",
)
@click.option(
    "--sqlite_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to the SQLite database file",
)
def main(sqlite_path: str) -> int:
    # Empty DB file → empty JSON
    if os.path.getsize(sqlite_path) == 0:
        with open("fastqc.json", "w") as fp:
            fp.write("{}")
        return 0

    # Query the new table
    cmd = ["sqlite3", sqlite_path, "SELECT * FROM fastqc_data_Basic_Statistics;"]

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
    except subprocess.CalledProcessError as e:
        click.echo(f"ERROR: SQLite query failed: {e}", err=True)
        return 1

    rows = output.split("\n")
    db_to_json(rows)
    return 0


if __name__ == "__main__":
    main()
