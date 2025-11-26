#!/usr/bin/env python

import json
import os
import subprocess
from typing import Any, Dict, List

import click


def db_to_json(result: List[str]) -> Dict[str, Any]:
    """
    Convert FastQC Basic Statistics output from SQLite into a JSON dictionary.

    Args:
        result: List of strings, each representing a row from
                'fastqc_data_Basic_Statistics', with '|' separators.

    Returns:
        Dictionary with filename as key and stats as nested dict.
    """
    data: Dict[str, Any] = {}
    filename: str = ""

    for line in result:
        line = line.strip()
        if not line:
            continue

        line_split = line.split("|")
        if len(line_split) < 5:
            continue  # skip malformed lines

        key = line_split[3].strip()
        value: Any = line_split[4].strip()

        # Start a new file entry
        if key == "Filename":
            filename = value
            data[filename] = {}
            continue

        if not filename:
            continue  # skip lines before a Filename appears

        # Convert numeric fields to int
        try:
            if key == "Sequence length" and "-" in value:
                value = max(int(x) for x in value.split("-"))
            elif key in ["Total Sequences", "Sequences flagged as poor quality", "%GC"]:
                value = int(value)
        except ValueError:
            value = None  # fallback if conversion fails

        data[filename][key] = value

    # Ensure at least an empty JSON object
    if not data:
        data = {}

    # Write JSON to file
    with open("fastqc.json", "w") as fp:
        import json

        json.dump(data, fp)

    return data


@click.command(
    context_settings=dict(help_option_names=["-h", "--help"]),
    help="Convert FastQC Basic Statistics from SQLite to JSON",
)
@click.option(
    "--sqlite_path",
    required=True,
    type=click.Path(exists=True),
    help="Path to FastQC SQLite file",
)
def main(sqlite_path: str) -> int:
    # If SQLite is empty, write empty JSON
    if os.path.getsize(sqlite_path) == 0:
        with open("fastqc.json", "w") as fp:
            json.dump({}, fp)
        return 0

    # Query SQLite safely without shell=True
    cmd = ["sqlite3", sqlite_path, "SELECT * FROM fastqc_data_Basic_Statistics;"]
    try:
        output = subprocess.check_output(cmd, shell=False).decode("utf-8")
    except subprocess.CalledProcessError:
        # If SQLite fails, still output empty JSON
        with open("fastqc.json", "w") as fp:
            json.dump({}, fp)
        return 0

    output_split = output.splitlines()
    db_to_json(output_split)
    return 0


if __name__ == "__main__":
    main()
