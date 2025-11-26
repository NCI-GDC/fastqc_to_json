#!/usr/bin/env python3

import unittest

from click.testing import CliRunner

from fastqc_to_json import main as MOD


class ThisTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_pass(self):
        with self.runner.isolated_filesystem():
            # create a dummy sqlite file
            with open("empty.sqlite", "wb") as f:
                pass

            result = self.runner.invoke(MOD.main, ["--sqlite_path", "empty.sqlite"])
            self.assertEqual(result.exit_code, 0)


# __END__
