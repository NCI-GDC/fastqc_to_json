#!/usr/bin/env python3

import json
import unittest

from click.testing import CliRunner

from fastqc_to_json import main


class ThisTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_db_to_json(self):
        with open("tests/test_data/test.fastqc", "r") as f:
            lines = f.readlines()
            result = main.db_to_json(lines)

        with open("tests/test_data/test.json", "r") as f:
            expected_results = json.load(f)

        assert expected_results == result


# __END__
