#!/usr/bin/env python

import json
import os
import subprocess
from typing import Any, Dict, List

import click


def db_to_json(result: List[str]) -> Dict[str, Any]:
    """
    Convert SQLite query output from FastQC Basic Statistics table into JSON.

    Args:
        result: List of strings, each string is a '|' delimited row from SQLite.

    Returns:
        Dictionary of filename -> statistics.
    """
    data: Dict[str, Any] = {}

    for line in result:
        if line == "":
            continue

        line_split = line.strip().split("|")
        key = line_split[3]
        value_str = line_split[4]  # always keep original string

        if key == "Filename":
            filename = value_str
            data[filename] = {}
        elif key in ["File type", "Encoding"]:
            data[filename][key] = value_str
        elif key in ["Total Sequences", "Sequences flagged as poor quality", "%GC"]:
            data[filename][key] = int(value_str)
        elif key == "Sequence length":
            if "-" in value_str:
                min_len, max_len = map(int, value_str.split("-"))
                data[filename][key] = max(min_len, max_len)
            else:
                data[filename][key] = int(value_str)

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp)

    return data


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="fastqc Basic Statistics to json",
)
@click.option(
    "--sqlite_path",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to the sqlite file",
)
def main(sqlite_path: str) -> int:
    """
    Convert a FastQC SQLite Basic Statistics table to JSON.
    """

    sqlite_size = os.path.getsize(sqlite_path)

    # Handle empty SQLite file
    if sqlite_size == 0:
        # Use subprocess to mimic Script 1 behavior
        subprocess.check_output(["touch", "fastqc.json"], shell=False)
        return 0

    # Handle non-empty SQLite file
    cmd = ["sqlite3", sqlite_path, '"select * from fastqc_data_Basic_Statistics;"']
    # shell_cmd = f'sqlite3 "{sqlite_path}" "select * from fastqc_data_Basic_Statistics;"'
    #   shell_cmd = " ".join(cmd)
    output = subprocess.check_output(cmd, shell=True).decode("utf-8")
    output_split = output.split("\n")
    db_to_json(output_split)

    return 0


if __name__ == "__main__":
    main()
