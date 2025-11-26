#!/usr/bin/env python

import json
import os
import sqlite3

# import subprocess
from typing import Any, Dict, List

import click


def db_to_json(result: List) -> Dict[str, Any]:
    data: Dict[str, Any] = dict()
    for line in result:
        if line == "":
            continue
        line_split = line.strip().split("|")
        key = line_split[3]
        value = line_split[4]
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
            if ("-") in value:
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
@click.option("--sqlite_path", required=True, type=click.Path(exists=True))
def main(sqlite_path: str) -> int:
    """Convert FastQC sqlite DB to JSON."""

    if os.path.getsize(sqlite_path) == 0:
        open("fastqc.json", "wb").close()
        return 0

    conn = sqlite3.connect(sqlite_path)
    try:
        rows = conn.execute("SELECT * FROM fastqc_data_Basic_Statistics").fetchall()
    finally:
        conn.close()

    output_split = []
    for row in rows:
        # convert row to list of strings
        parts = [str(c) for c in row]

        # ensure at least 5 fields
        while len(parts) < 5:
            parts.insert(0, "")

        output_split.append("|".join(parts[:5]))

    db_to_json(output_split)
    return 0


if __name__ == "__main__":
    main()
