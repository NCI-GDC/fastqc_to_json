#!/usr/bin/env python3

import json
import os
import subprocess
import sys
from typing import Any, List, Optional

OUTPUT_JSON = "fastqc.json"


def run_sqlite_query(sqlite_path: str) -> List[str]:
    """
    Run the exact query required for the broken fastqc_data_Basic_Statistics schema.
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
            ["sqlite3", sqlite_path, query],
            stderr=subprocess.STDOUT,
        ).decode("utf-8")
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"ERROR: sqlite3 failed:\n{e.output.decode()}\n")
        sys.exit(1)

    return [line for line in output.splitlines() if line.strip()]


def coerce_value(raw: str) -> Any:
    """
    Convert SQLite text values to int / float when appropriate.
    """
    try:
        if "." in raw:
            f = float(raw)
            return int(f) if f.is_integer() else f
        return int(raw)
    except ValueError:
        return raw


def db_to_json(rows: list[str]) -> dict[str, dict[str, object]]:
    data: dict[str, dict[str, object]] = {}

    for line in rows:
        parts = line.split("|")
        if len(parts) < 9:
            continue

        fastq = parts[6]
        measure = parts[7]
        raw_value = parts[8]

        if fastq not in data:
            data[fastq] = {}

        if raw_value.isdigit():
            value: object = int(raw_value)
        else:
            try:
                value = float(raw_value)
            except ValueError:
                value = raw_value

        data[fastq][measure] = value

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp, indent=2)

    return data


def resolve_sqlite_path() -> Optional[str]:
    """
    Resolve the SQLite path in CWL/Docker-safe order:
    1. First positional argument
    2. SQLITE_PATH env var
    3. Fail clearly
    """
    if len(sys.argv) > 1:
        return sys.argv[1]

    env_path = os.environ.get("SQLITE_PATH")
    if env_path:
        return env_path

    return None


def main() -> int:
    sqlite_path = resolve_sqlite_path()

    if not sqlite_path:
        sys.stderr.write(
            "ERROR: No SQLite DB path provided.\n"
            "Provide as positional argument or set SQLITE_PATH.\n"
        )
        return 1

    if not os.path.exists(sqlite_path):
        sys.stderr.write(f"ERROR: SQLite DB not found: {sqlite_path}\n")
        return 1

    if os.path.getsize(sqlite_path) == 0:
        # Empty DB → empty JSON (explicit)
        with open(OUTPUT_JSON, "w") as fp:
            fp.write("{}")
        return 0

    rows = run_sqlite_query(sqlite_path)

    data = db_to_json(rows)

    if not data:
        sys.stderr.write(
            "ERROR: Database contained rows but produced empty JSON.\n"
            "Schema mismatch or unexpected data format.\n"
        )
        return 1

    with open(OUTPUT_JSON, "w") as fp:
        json.dump(data, fp, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
