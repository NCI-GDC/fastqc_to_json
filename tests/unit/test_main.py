import json
import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from fastqc_to_json import main as MOD


@pytest.fixture
def runner():
    """Provide a Click test runner."""
    return CliRunner()


def test_empty_sqlite_creates_json(runner):
    """
    Test that an empty SQLite file results in a zero-byte fastqc.json file
    and exits cleanly.
    """
    with runner.isolated_filesystem():
        # Create empty SQLite file
        sqlite_file = "empty.db"
        with open(sqlite_file, "w") as f:
            f.write("")

        # Run the CLI
        result = runner.invoke(MOD.main, ["--sqlite_path", sqlite_file])
        assert result.exit_code == 0

        # fastqc.json should exist (even if zero bytes)
        json_file = "fastqc.json"
        assert json_file in os.listdir(".")


@patch("fastqc_to_json.main.subprocess.check_output")
def test_populated_sqlite_creates_json(mock_subproc, runner):
    """
    Test that a populated SQLite output is correctly converted to JSON.
    """
    # Mock the SQLite output
    mock_output = (
        "1|2|3|Filename|sample1.fastq\n"
        "1|2|3|File type|fastq\n"
        "1|2|3|Encoding|Sanger\n"
        "1|2|3|Total Sequences|100\n"
        "1|2|3|Sequences flagged as poor quality|5\n"
        "1|2|3|Sequence length|50-100\n"
        "1|2|3|%GC|60\n"
    )
    mock_subproc.return_value = mock_output.encode("utf-8")

    with runner.isolated_filesystem():
        # Create dummy SQLite file
        sqlite_file = "populated.db"
        with open(sqlite_file, "w") as f:
            f.write("dummy content")

        # Run the CLI
        result = runner.invoke(MOD.main, ["--sqlite_path", sqlite_file])
        assert result.exit_code == 0

        # Check fastqc.json contents
        with open("fastqc.json", "r") as f:
            data = json.load(f)

        assert "sample1.fastq" in data
        assert data["sample1.fastq"]["File type"] == "fastq"
        assert data["sample1.fastq"]["Encoding"] == "Sanger"
        assert data["sample1.fastq"]["Total Sequences"] == 100
        assert data["sample1.fastq"]["Sequences flagged as poor quality"] == 5
        assert data["sample1.fastq"]["Sequence length"] == 100  # max of 50-100
        assert data["sample1.fastq"]["%GC"] == 60
