import json
import os
import tempfile

from fastqc_to_json.main import db_to_json


def test_db_to_json_parses_fastqc_basic_stats():
    # Simulated sqlite3 output for the NEW schema:
    # job_uuid | fastq | Measure | Value
    sample_rows = [
        "uuid|sample_1.fastq.gz|File type|Conventional base calls",
        "uuid|sample_1.fastq.gz|Encoding|Sanger / Illumina 1.9",
        "uuid|sample_1.fastq.gz|Total Sequences|123456",
        "uuid|sample_1.fastq.gz|Sequences flagged as poor quality|12",
        "uuid|sample_1.fastq.gz|Sequence length|101",
        "uuid|sample_1.fastq.gz|%GC|45",
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
