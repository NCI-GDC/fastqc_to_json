import os
import sqlite3
import tempfile

from fastqc_to_json.main import OUTPUT_JSON, db_to_json


def test_db_to_json_creates_json_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table matching your schema
        cursor.execute(
            """
            CREATE TABLE fastqc_data_Basic_Statistics (
                job_uuid TEXT,
                fastq TEXT,
                Measure TEXT,
                Value TEXT
            );
            """
        )

        # Insert test rows
        cursor.executemany(
            "INSERT INTO fastqc_data_Basic_Statistics VALUES (?, ?, ?, ?)",
            [
                ("uuid", "sample_1.fastq.gz", "Total Sequences", "123456"),
                ("uuid", "sample_1.fastq.gz", "Sequence length", "101"),
                ("uuid", "sample_1.fastq.gz", "%GC", "45"),
            ],
        )
        conn.commit()
        conn.close()

        # Change working directory to tmpdir so OUTPUT_JSON is written there
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            data = db_to_json(db_path)
            # JSON file should exist
            assert os.path.exists(OUTPUT_JSON)
            # JSON content is correct
            assert "sample_1.fastq.gz" in data
            assert data["sample_1.fastq.gz"]["Total Sequences"] == 123456
            assert data["sample_1.fastq.gz"]["Sequence length"] == 101
            assert data["sample_1.fastq.gz"]["%GC"] == 45
        finally:
            os.chdir(old_cwd)
