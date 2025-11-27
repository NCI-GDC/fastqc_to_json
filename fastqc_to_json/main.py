#!/usr/bin/env python

import argparse
import json
import os
import subprocess
from typing import Dict, List, Optional, Union


def db_to_json(result: List[str]) -> None:
    data: Dict[str, Dict[str, Union[int, str]]] = dict()
    filename: Optional[str] = None

    for line in result:
        if line == "":
            continue

        parts = line.strip().split("|")
        if len(parts) < 5:
            continue

        key = parts[3]
        value = parts[4]

        if key == "Filename":
            filename = value
            data[filename] = dict()
        elif filename is not None:
            if key in ("File type", "Encoding"):
                data[filename][key] = value
            elif key in ("Total Sequences", "Sequences flagged as poor quality", "%GC"):
                data[filename][key] = int(value)
            elif key == "Sequence length":
                if "-" in value:
                    nums = [int(x) for x in value.split("-")]
                    value_int = max(nums)
                else:
                    value_int = int(value)
                data[filename][key] = value_int

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp)


def main() -> None:
    parser = argparse.ArgumentParser("fastqc Basic Statistics to json")

    parser.add_argument("--sqlite_path", required=True)

    args = parser.parse_args()
    sqlite_path: str = args.sqlite_path

    sqlite_size: int = os.path.getsize(sqlite_path)
    if sqlite_size == 0:
        subprocess.check_output(["touch", "fastqc.json"], shell=False)
        return

    cmd = ["sqlite3", sqlite_path, '"select * from fastqc_data_Basic_Statistics;"']
    shell_cmd = " ".join(cmd)

    output: str = subprocess.check_output(shell_cmd, shell=True).decode("utf-8")
    output_split: List[str] = output.split("\n")

    db_to_json(output_split)


if __name__ == "__main__":
    main()
