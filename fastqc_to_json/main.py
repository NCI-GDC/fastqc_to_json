#!/usr/bin/env python

import argparse
import json
import logging
import os
import subprocess

log = logging.getLogger(__name__)


def db_to_json(result_lines):
    data = {}
    filename = None

    for line in result_lines:
        if not line.strip():
            continue

        parts = line.strip().split("|")
        if len(parts) < 5:
            continue

        _, _, _, key, value = parts

        if key == "Filename":
            filename = value
            data[filename] = {}
        elif filename is not None:
            if key in ("File type", "Encoding"):
                data[filename][key] = value
            elif key in ("Total Sequences", "Sequences flagged as poor quality", "%GC"):
                data[filename][key] = int(value)
            elif key == "Sequence length":
                if "-" in value:
                    value = max(int(v) for v in value.split("-"))
                data[filename][key] = int(value)

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp)

    return


def main() -> int:
    """Main CLI logic. Returns exit code."""
    parser = argparse.ArgumentParser("fastqc Basic Statistics to json")

    parser.add_argument("--sqlite_path", required=True)

    args = parser.parse_args()
    sqlite_path = args.sqlite_path

    # If file empty → create empty JSON
    if os.path.getsize(sqlite_path) == 0:
        open("fastqc.json", "w").close()
        return 0

    # Run sqlite query
    try:
        output = subprocess.check_output(
            ["sqlite3", sqlite_path, "select * from fastqc_data_Basic_Statistics;"],
            text=True,
        )
    except subprocess.CalledProcessError as e:
        log.error("SQLite query failed: %s", e)
        return 1

    db_to_json(output.splitlines())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
