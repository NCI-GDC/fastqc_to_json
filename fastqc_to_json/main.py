#!/usr/bin/env python3

import json
import os
import subprocess
from typing import Any, Dict, Iterable, List, Optional, Union

import click


def _parse_rows(rows: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    """
    Shared parser for FastQC Basic Statistics rows.

    Expected row format:
        job_uuid|fastq|Measure|Value
    """
    data: Dict[str, Dict[str, Any]] = {}

    for line in rows:
        line = line.strip()
        if not line:
            continue

        parts = line.split("|")
        if len(parts) != 4:
            continue

        _job_uuid, fastq, measure, raw_value = parts

        if fastq not in data:
            data[fastq] = {}

        # Robust numeric conversion
        try:
            if "." in raw_value:
                f = float(raw_value)
                value: Any = int(f) if f.is_integer() else f
            else:
                value = int(raw_value)
        except ValueError:
            value = raw_value

        data[fastq][measure] = value

    return data


def db_to_json(source: Union[str, List[str]]) -> None:
    """
    Convert FastQC Basic Statistics into fastqc.json.

    Accepts either:
      - List[str] of sqlite output rows (unit tests)
      - Path to sqlite database (runtime / container)
    """

    # ---- TEST MODE ----
    if isinstance(source, list):
        data = _parse_rows(source)
        with open("fastqc.json", "w") as fp:
            json.dump(data, fp, indent=2)
        return

    # ---- RUNTIME MODE ----
    sqlite_path = source

    # Empty or missing DB → empty JSON
    if not os.path.exists(sqlite_path) or os.path.getsize(sqlite_path) == 0:
        with open("fastqc.json", "w") as fp:
            fp.write("{}")
        return

    cmd = [
        "sqlite3",
        sqlite_path,
        "SELECT job_uuid, fastq, Measure, Value FROM fastqc_data_Basic_Statistics;",
    ]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"SQLite query failed: {exc.output.decode('utf-8')}"
        ) from exc

    rows = output.splitlines()
    data = _parse_rows(rows)

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp, indent=2)


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="Convert fastqc_data_Basic_Statistics table into JSON (NEW DB STRUCTURE).",
)
@click.option(
    "--sqlite_path",
    "--INPUT",
    required=False,
    type=click.Path(exists=True),
    help="Path to the SQLite database file (optional).",
)
def main(sqlite_path: Optional[str] = None) -> int:
    """
    If sqlite_path is provided, converts DB → JSON.
    If called without arguments, does nothing (safe for tests).
    """
    if sqlite_path:
        db_to_json(sqlite_path)
    return 0


if __name__ == "__main__":
    main()
