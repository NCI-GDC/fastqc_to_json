from unittest.mock import mock_open, patch

from click.testing import CliRunner

# import subprocess
from fastqc_to_json.main import main as fastqc_main


def test_main_empty_sqlite_creates_empty_json(tmp_path, monkeypatch):
    runner = CliRunner()
    sqlite_path = tmp_path / "empty.sqlite"
    sqlite_path.touch()

    # Patch getsize to simulate empty file
    monkeypatch.setattr("os.path.getsize", lambda path: 0)

    # Patch open to avoid writing a real file
    with patch("builtins.open", mock_open()) as mocked_file:
        result = runner.invoke(fastqc_main, ["--sqlite_path", str(sqlite_path)])
        assert result.exit_code == 0
        mocked_file.assert_called_once_with("fastqc.json", "w")


def test_main_with_data(tmp_path, monkeypatch):
    runner = CliRunner()
    sqlite_path = tmp_path / "data.sqlite"
    sqlite_path.write_text("dummy")

    monkeypatch.setattr("os.path.getsize", lambda path: 10)

    # Sample output simulating sqlite3 query result
    sample_output = (
        "|x|y|z|Filename|abc.fastq|\n"
        "|x|y|z|File type|FastQ|\n"
        "|x|y|z|Encoding|Sanger|\n"
        "|x|y|z|Total Sequences|50|\n"
        "|x|y|z|Sequences flagged as poor quality|5|\n"
        "|x|y|z|Sequence length|100|\n"
        "|x|y|z|%GC|40|\n"
    )

    with patch("subprocess.check_output", return_value=sample_output.encode("utf-8")):
        with patch("builtins.open", mock_open()) as mocked_file:
            result = runner.invoke(fastqc_main, ["--sqlite_path", str(sqlite_path)])
            assert result.exit_code == 0
            mocked_file.assert_called()  # fastqc.json is written
