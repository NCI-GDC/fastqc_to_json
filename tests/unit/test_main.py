#!/usr/bin/env python3

import os
import unittest

from click.testing import CliRunner

from fastqc_to_json import main as MOD


class ThisTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_pass(self):
        #        result = self.runner.invoke(MOD.main)
        #        result = self.runner.invoke(MOD.main, ["--sqlite_path", "/tmp/fake.db"])
        #        self.assertEqual(result.exit_code, 0)

        dummy_db = "/tmp/fake.db"
        with open(dummy_db, "w") as f:
            f.write("")  # empty file

        result = self.runner.invoke(MOD.main, ["--sqlite_path", dummy_db])
        self.assertEqual(result.exit_code, 0)
        # Clean up
        os.remove(dummy_db)


# __END__
