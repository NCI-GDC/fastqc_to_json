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
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="path of sqlite file",
)
def main(sqlite_path: str) -> int:
    # if no data, then output zero byte json file
    sqlite_size = os.path.getsize(sqlite_path)
    if sqlite_size == 0:
        cmd = ["touch", "fastqc.json"]
        output = subprocess.check_output(cmd, shell=False)
        return 0

    # if data, then output populated json
    cmd = ["sqlite3", sqlite_path, '"select * from fastqc_data_Basic_Statistics;"']
    shell_cmd = " ".join(cmd)
    output = subprocess.check_output(shell_cmd, shell=True).decode("utf-8")  # type: ignore
    output_split = output.split("\n")  # type: ignore
    db_to_json(output_split)
    return 0


if __name__ == "__main__":
    main()
