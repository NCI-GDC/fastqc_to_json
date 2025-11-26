import os
import sqlite3
import unittest

from click.testing import CliRunner

from fastqc_to_json import main as MOD


class TestFastqcToJson(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_empty_sqlite(self):
        """Test that a zero-byte sqlite file produces an empty JSON output."""
        with self.runner.isolated_filesystem():
            # create an empty 0-byte sqlite file
            open("empty.sqlite", "wb").close()

            result = self.runner.invoke(MOD.main, ["--sqlite_path", "empty.sqlite"])

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.exists("fastqc.json"))
            self.assertEqual(os.path.getsize("fastqc.json"), 0)

    def test_nonempty_sqlite(self):
        """Test that a sqlite DB with the expected table produces JSON output."""
        with self.runner.isolated_filesystem():
            # Create a sqlite DB containing expected table & one row
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

            result = self.runner.invoke(MOD.main, ["--sqlite_path", "test.sqlite"])

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.exists("fastqc.json"))
            # File should not be empty now
            self.assertGreater(os.path.getsize("fastqc.json"), 0)
