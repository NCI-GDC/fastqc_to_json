import json
import os
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from fastqc_to_json import main as MOD


@pytest.fixture
def runner():
    return CliRunner()


def test_empty_sqlite_creates_json(runner):
    """Test that an empty SQLite file results in a zero-byte fastqc.json file."""
    with runner.isolated_filesystem():
        sqlite_file = "empty.db"
        open(sqlite_file, "w").close()

        # Mock subprocess.check_output for touch command
        with patch("fastqc_to_json.main.subprocess.check_output") as mock_subproc:

            def touch_side_effect(cmd, shell):
                # simulate 'touch fastqc.json'
                open("fastqc.json", "w").close()
                return b""

            mock_subproc.side_effect = touch_side_effect

            result = runner.invoke(MOD.main, ["--sqlite_path", sqlite_file])
            assert result.exit_code == 0
            assert "fastqc.json" in os.listdir(".")


@patch("fastqc_to_json.main.subprocess.check_output")
def test_populated_sqlite_creates_json(mock_subproc, runner):
    """Test that a populated SQLite output is correctly converted to JSON."""
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
        sqlite_file = "populated.db"
        # non-empty file so main calls db_to_json
        with open(sqlite_file, "w") as f:
            f.write("x")

        result = runner.invoke(MOD.main, ["--sqlite_path", sqlite_file])
        assert result.exit_code == 0

        with open("fastqc.json", "r") as f:
            data = json.load(f)

        assert "sample1.fastq" in data
        assert data["sample1.fastq"]["File type"] == "fastq"
        assert data["sample1.fastq"]["Encoding"] == "Sanger"
        assert data["sample1.fastq"]["Total Sequences"] == 100
        assert data["sample1.fastq"]["Sequences flagged as poor quality"] == 5
        assert data["sample1.fastq"]["Sequence length"] == 100
        assert data["sample1.fastq"]["%GC"] == 60
