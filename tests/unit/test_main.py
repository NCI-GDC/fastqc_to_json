import json
import os
import sqlite3

from click.testing import CliRunner

from fastqc_to_json.main import main as cli_main


class TestFastqcToJson:
    def setup_method(self):
        self.runner = CliRunner()

    def test_empty_sqlite(self):
        """When the sqlite file is empty, fastqc.json should be created and empty."""
        with self.runner.isolated_filesystem():
            open("test.sqlite", "wb").close()

            result = self.runner.invoke(cli_main, ["--sqlite_path", "test.sqlite"])
            assert result.exit_code == 0, result.output

            assert os.path.exists("fastqc.json")
            with open("fastqc.json") as f:
                data = f.read().strip()
                assert data in ("", "{}")

    def test_nonempty_sqlite(self):
        """A sqlite DB with the expected table produces correct JSON."""
        with self.runner.isolated_filesystem():
            conn = sqlite3.connect("test.sqlite")
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE fastqc_data_Basic_Statistics (key TEXT, value TEXT)"
            )

            cur.execute(
                "INSERT INTO fastqc_data_Basic_Statistics VALUES (?, ?)",
                ("Filename", "sample1"),
            )
            cur.execute(
                "INSERT INTO fastqc_data_Basic_Statistics VALUES (?, ?)",
                ("Total Sequences", "12345"),
            )
            conn.commit()
            conn.close()

            result = self.runner.invoke(cli_main, ["--sqlite_path", "test.sqlite"])
            assert result.exit_code == 0, result.output

            assert os.path.exists("fastqc.json")
            with open("fastqc.json") as f:
                data = json.load(f)

            assert data == {"sample1": {"Total Sequences": 12345}}
