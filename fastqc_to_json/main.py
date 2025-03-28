#!/usr/bin/env python

import argparse
import json
import os
import subprocess


def db_to_json(result):
    data = dict()
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
    return


def main():
    parser = argparse.ArgumentParser("fastqc Basic Statistics to json")

    # Required flags.
    parser.add_argument("--sqlite_path", required=True)

    # setup required parameters
    args = parser.parse_args()
    sqlite_path = args.sqlite_path

    # if no data, then output zero byte json file
    sqlite_size = os.path.getsize(sqlite_path)
    if sqlite_size == 0:
        cmd = ["touch", "fastqc.json"]
        output = subprocess.check_output(cmd, shell=False)
        return

    # if data, then output populated json
    cmd = ["sqlite3", sqlite_path, '"select * from fastqc_data_Basic_Statistics;"']
    shell_cmd = " ".join(cmd)
    output = subprocess.check_output(shell_cmd, shell=True).decode("utf-8")
    output_split = output.split("\n")
    db_to_json(output_split)
    return


if __name__ == "__main__":
    main()
