#!/usr/bin/env python

import json
import os
import subprocess
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
@click.option(
    "--sqlite_path",
    help="path of sqlite file",
    required=True,
    type=click.Path(exists=True),
)
def main(sqlite_path):
    """Convert FastQC sqlite DB to JSON."""

    sqlite_size = os.path.getsize(sqlite_path)

    # If empty DB, create empty JSON file
    if sqlite_size == 0:
        subprocess.check_call(["touch", "fastqc.json"])
        return

    # Extract data with sqlite3
    query = "select * from fastqc_data_Basic_Statistics;"
    cmd = f'sqlite3 "{sqlite_path}" "{query}"'
    output = subprocess.check_output(cmd, shell=True).decode("utf-8")

    output_split = output.split("\n")
    db_to_json(output_split)


if __name__ == "__main__":
    main()
