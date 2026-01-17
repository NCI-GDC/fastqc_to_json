#!/usr/bin/env python3

import argparse
import json
import logging
import os

import sqlalchemy
from sqlalchemy import text

from .fastqc_db import fastqc_db


def db_to_json(engine: sqlalchemy.Engine) -> None:
    """
    Mirror the original sqlite3-based script as closely as possible.
    Output is always valid JSON (never empty).
    """
    data = {}
    filename = None

    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM fastqc_data_Basic_Statistics")
        ).fetchall()

    # Original behavior: empty DB → empty JSON object
    if not rows:
        with open("fastqc.json", "w") as fp:
            json.dump({}, fp)
        return

    for row in rows:
        # Match original column usage exactly
        key = row[3]
        value = row[4]

        if not key or value is None:
            continue

        if key == "Filename":
            filename = value
            data[filename] = {}

        elif filename is None:
            continue

        elif key in ("File type", "Encoding"):
            data[filename][key] = value

        elif key in (
            "Total Sequences",
            "Sequences flagged as poor quality",
            "%GC",
        ):
            try:
                data[filename][key] = int(value)
            except ValueError:
                pass

        elif key == "Sequence length":
            if "-" in value:
                try:
                    value = max(int(x) for x in value.split("-"))
                except ValueError:
                    continue
            try:
                data[filename][key] = int(value)
            except ValueError:
                pass

    with open("fastqc.json", "w") as fp:
        json.dump(data, fp)


def main() -> int:
    parser = argparse.ArgumentParser("fastqc Basic Statistics to json")

    parser.add_argument("--job_uuid", required=True)
    parser.add_argument("--INPUT", required=True)

    args = parser.parse_args()

    fastqc_zip_path = args.INPUT
    fastqc_zip_base = os.path.splitext(os.path.basename(fastqc_zip_path))[0]

    sqlite_name = f"{fastqc_zip_base}.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{sqlite_name}")

    # Run the existing DB creator unchanged
    fastqc_db(args.job_uuid, fastqc_zip_path, engine, logging.getLogger(__name__))

    # Convert DB → JSON (old behavior)
    db_to_json(engine)

    # Safety net: guarantee file exists and is valid JSON
    if not os.path.exists("fastqc.json"):
        with open("fastqc.json", "w") as fp:
            json.dump({}, fp)

    return 0


if __name__ == "__main__":
    main()
