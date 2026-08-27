import json
import os
import tempfile

from fastqc_to_json.main import db_to_json


def test_db_to_json_creates_json_file():
    result = [
        ("uuid", "sample_1.fastq.gz", "Filename", "sample_1.fastq.gz"),
        ("uuid", "sample_1.fastq.gz", "Total Sequences", "123456"),
        ("uuid", "sample_1.fastq.gz", "Sequence length", "101"),
        ("uuid", "sample_1.fastq.gz", "%GC", "45"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            data = db_to_json(result)

            assert os.path.exists("fastqc.json")

            assert "sample_1.fastq.gz" in data
            assert data["sample_1.fastq.gz"]["Total Sequences"] == 123456
            assert data["sample_1.fastq.gz"]["Sequence length"] == 101
            assert data["sample_1.fastq.gz"]["%GC"] == 45

            with open("fastqc.json") as fp:
                written_data = json.load(fp)

            assert written_data == data

        finally:
            os.chdir(old_cwd)


def test_sequence_length_range_uses_upper_bound():
    result = [
        ("uuid", "sample_1.fastq.gz", "Filename", "sample_1.fastq.gz"),
        ("uuid", "sample_1.fastq.gz", "Sequence length", "15-51"),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)

        try:
            data = db_to_json(result)

            assert data["sample_1.fastq.gz"]["Sequence length"] == 51

        finally:
            os.chdir(old_cwd)
