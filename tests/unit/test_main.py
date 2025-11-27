import json
import os
import tempfile

from fastqc_to_json.main import db_to_json


def test_db_to_json_parses_fastqc_basic_stats():
    # Simulated sqlite3 output matching your real schema:
    # cols: 0 | 1 | 2 | 3 | 4 | 5 |      6        |      7      |      8
    sample_rows = [
        "0|uuid|fastq|x|x|x|sample_1.fastq.gz|Filename|sample_1.fastq.gz",
        "1|uuid|fastq|x|x|x|sample_1.fastq.gz|File type|Conventional base calls",
        "2|uuid|fastq|x|x|x|sample_1.fastq.gz|Encoding|Sanger / Illumina 1.9",
        "3|uuid|fastq|x|x|x|sample_1.fastq.gz|Total Sequences|123456",
        "4|uuid|fastq|x|x|x|sample_1.fastq.gz|Sequences flagged as poor quality|12",
        "5|uuid|fastq|x|x|x|sample_1.fastq.gz|Sequence length|101",
        "6|uuid|fastq|x|x|x|sample_1.fastq.gz|%GC|45",
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            db_to_json(sample_rows)

            assert os.path.exists("fastqc.json")

            with open("fastqc.json") as fp:
                data = json.load(fp)

            assert "sample_1.fastq.gz" in data
            stats = data["sample_1.fastq.gz"]

            assert stats["File type"] == "Conventional base calls"
            assert stats["Encoding"] == "Sanger / Illumina 1.9"
            assert stats["Total Sequences"] == 123456
            assert stats["Sequences flagged as poor quality"] == 12
            assert stats["Sequence length"] == 101
            assert stats["%GC"] == 45

        finally:
            os.chdir(cwd)
