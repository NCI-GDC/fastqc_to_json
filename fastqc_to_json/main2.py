#!/usr/bin/env python

import argparse
import json
import os
import subprocess
from typing import Any, Dict, List


def db_to_json(rows: List[str]) -> None:
    """
    Convert SQLite row strings to fastqc.json structure.
    Rows are expected in the format:
        index|job_uuid|fastq|col3|col4|col5|filename|measure|value
    """
    data: Dict[str, Dict[str, Any]] = {}

    for line in rows:
        parts = line.strip().split("|")
        if len(parts) < 9:
            continue

        filename = parts[6]
        measure = parts[7]
        raw_value = parts[8]

        if filename not in data:
            data[filename] = {}

        # Typed value holder
        value: Any = raw_value

        # Attempt numeric conversion
        num_candidate = raw_value.replace(".", "", 1)
        if num_candidate.isdigit():
            try:
                if "." in raw_value:
                    f = float(raw_value)
                    value = int(f) if f.is_integer() else f
                else:
                    value = int(raw_value)
            except ValueError:
                value = raw_value

        data[filename][measure] = value

    # Write output JSON
    with open("fastqc.json", "w") as fp:
        json.dump(data, fp, indent=2)


def main() -> int:
    """
    CLI entrypoint. Behaves exactly like the original script but returns an int.
    """
    parser = argparse.ArgumentParser("fastqc Basic Statistics to json")
    parser.add_argument("--sqlite_path", required=True)
    args = parser.parse_args()

    sqlite_path = args.sqlite_path

    # If SQLite file exists but contains no data → write empty JSON
    if os.path.getsize(sqlite_path) == 0:
        subprocess.check_output(["touch", "fastqc.json"])
        return 0

    # Query Basic Statistics table (same as original)
    cmd = ["sqlite3", sqlite_path, "SELECT * FROM fastqc_data_Basic_Statistics;"]

    output = subprocess.check_output(cmd).decode("utf-8")
    rows = output.split("\n")

    db_to_json(rows)
    return 0


if __name__ == "__main__":
    main()
