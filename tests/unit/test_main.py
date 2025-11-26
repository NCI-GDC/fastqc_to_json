import json
import os
import sqlite3

from click.testing import CliRunner

from fastqc_to_json.main import main as cli_main


class TestFastqcToJson:
    def setUp(self):
        self.runner = CliRunner()

    def test_empty_sqlite(self):
        """When the sqlite file is empty, fastqc.json should be created and empty."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create empty sqlite file
            open("test.sqlite", "wb").close()

            result = runner.invoke(cli_main, ["--sqlite_path", "test.sqlite"])
            assert result.exit_code == 0, result.output

            # fastqc.json should exist and be empty JSON {}
            assert os.path.exists("fastqc.json")

            with open("fastqc.json") as f:
                data = f.read()
                assert data.strip() == "" or data.strip() == "{}"

    def test_nonempty_sqlite(self):
        """A sqlite DB with the expected table produces correct JSON."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            # Create DB with the expected table & one row
            conn = sqlite3.connect("test.sqlite")
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE fastqc_data_Basic_Statistics (key TEXT, value TEXT)"
            )
            cur.execute(
                "INSERT INTO fastqc_data_Basic_Statistics VALUES (?, ?)",
                ("Total Sequences", "12345"),
            )
            conn.commit()
            conn.close()

            result = runner.invoke(cli_main, ["--sqlite_path", "test.sqlite"])
            assert result.exit_code == 0, result.output

            # fastqc.json must exist
            assert os.path.exists("fastqc.json")

            # Validate JSON contents
            with open("fastqc.json") as f:
                data = json.load(f)

            assert data == {"Total Sequences": "12345"}
