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
        json.dump(data, fp, indent=2)

    return data


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="fastqc Basic Statistics to json",
)
@click.option("--sqlite_path", type=str, required=True, help="path of sqlite file")
def main(sqlite_path: str) -> int:
    if os.path.getsize(sqlite_path) == 0:
        open("fastqc.json", "w").close()
        return 0

    cmd = ["sqlite3", sqlite_path, "select * from fastqc_data_Basic_Statistics;"]

    try:
        output = subprocess.check_output(cmd).decode("utf-8")
    except subprocess.CalledProcessError:
        open("fastqc.json", "w").close()
        return 0

    rows = output.strip().split("\n") if output else []

    if not rows:
        open("fastqc.json", "w").close()
        return 0

    db_to_json(rows)
    return 0


if __name__ == "__main__":
    main()
