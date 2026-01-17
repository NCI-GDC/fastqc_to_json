#!/usr/bin/env python

import argparse
import json
import logging
import os
import sqlite3
import sys
from typing import Any, Dict, Iterable, Optional, Union

LOG = logging.getLogger(__name__)


def _parse_rows(rows: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    """
    Parse pipe-delimited rows:
    job_uuid | fastq | Measure | Value
    """
    data: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        parts = row.split("|")
        if len(parts) != 4:
            continue

        _, fastq, key, raw_value = parts

        if fastq not in data:
            data[fastq] = {}

        # String fields
        if key in ("File type", "Encoding"):
            data[fastq][key] = raw_value
            continue

        # Integer fields
        if key in (
            "Total Sequences",
            "Sequences flagged as poor quality",
            "%GC",
        ):
            try:
                data[fastq][key] = int(raw_value)
            except ValueError:
                continue
            continue

        # Sequence length (may be range like 36-101)
        if key == "Sequence length":
            value: Optional[int]

            if "-" in raw_value:
                try:
                    value = max(int(v) for v in raw_value.split("-"))
                except ValueError:
                    continue
            else:
                try:
                    value = int(raw_value)
                except ValueError:
                    continue

            data[fastq][key] = value

    return data


def db_to_json(source: Union[str, Iterable[str]]) -> None:
    """
    Convert FastQC Basic Statistics into fastqc.json.

    Accepts either:
      - sqlite database path (runtime)
      - iterable of pipe-delimited rows (test mode)
    """

    #  TEST MODE (pytest passes rows directly)
    if not isinstance(source, (str, bytes, os.PathLike)):
        data = _parse_rows(source)
        with open("fastqc.json", "w") as fh:
            json.dump(data, fh)
        return

    # RUNTIME MODE (sqlite database)
    sqlite_path = source

    if not os.path.exists(sqlite_path) or os.path.getsize(sqlite_path) == 0:
        with open("fastqc.json", "w") as fh:
            json.dump({}, fh)
        return

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT job_uuid, fastq, Measure, Value FROM fastqc_data_Basic_Statistics"
        )
        rows = ["|".join(map(str, row)) for row in cursor.fetchall()]
    except sqlite3.Error:
        rows = []
    finally:
        conn.close()

    data = _parse_rows(rows)

    with open("fastqc.json", "w") as fh:
        json.dump(data, fh)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="fastqc Basic Statistics to json")
    parser.add_argument("--job_uuid", required=True)
    parser.add_argument("--INPUT", required=True)

    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)
    LOG.info("Version: %s", "0.1.1")
    LOG.info("Process called with %s", sys.argv)

    db_to_json(args.INPUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
