#!/usr/bin/env python

import json
import os
import subprocess
from typing import Any, Dict, List

import click


def db_to_json(result: List[str]) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    filename = None

    for line in result:
        if not line.strip():
            continue

        line_split = line.strip().split("|")
        if len(line_split) < 5:
            continue

        key = line_split[3]
        value = line_split[4]

        if key == "Filename":
            filename = value
            data[filename] = {}
        elif filename:
            if key in ["File type", "Encoding"]:
                data[filename][key] = value
            elif key in ["Total Sequences", "Sequences flagged as poor quality", "%GC"]:
                data[filename][key] = int(value)
            elif key == "Sequence length":
                if "-" in value:
                    value = max(int(x) for x in value.split("-"))
                else:
                    value = int(value)
                data[filename][key] = value

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp, indent=2)

    return data


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="fastqc Basic Statistics to json",
)
@click.option("--sqlite_path", type=str, required=True, help="path of sqlite file")
def main(sqlite_path: str) -> int:
    # If SQLite file is empty → produce empty JSON (workflow expects it)
    if os.path.getsize(sqlite_path) == 0:
        open("fastqc.json", "w").close()
        return 0

    # Run sqlite3 safely
    cmd = ["sqlite3", sqlite_path, "select * from fastqc_data_Basic_Statistics;"]

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
    except subprocess.CalledProcessError as e:
        # If sqlite fails, produce empty JSON but DO NOT crash the workflow
        open("fastqc.json", "w").close()
        return 0

    rows = output.strip().split("\n") if output else []

    if not rows:
        # Table empty → generate empty json
        open("fastqc.json", "w").close()
        return 0

    db_to_json(rows)
    return 0


if __name__ == "__main__":
    main()
