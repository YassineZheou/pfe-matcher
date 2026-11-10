import contextlib
import csv
import io
import json
import os
import tempfile
import unittest

from pfe_matcher import cli, store
from pfe_matcher.parser import parse_topics
from tests.helpers import SAMPLE_PDF, SAMPLE_TXT


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.dir.name, "t.db")

    def tearDown(self):
        self.dir.cleanup()

    def test_roundtrip(self):
        topics = parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))
        store.replace_topics(self.db, topics)
        loaded = store.load_topics(self.db)
        self.assertEqual(len(loaded), 8)
        self.assertEqual(loaded[0].skills, topics[0].skills)

    def test_replace_overwrites(self):
        topics = parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))
        store.replace_topics(self.db, topics)
        store.replace_topics(self.db, topics[:2])
        self.assertEqual(len(store.load_topics(self.db)), 2)

    def test_export_csv(self):
        topics = parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))
        target = os.path.join(self.dir.name, "out.csv")
        store.export_csv(topics, target)
        with open(target, encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle, delimiter=";"))
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[0][0], "ref")


class CliTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.dir.name, "t.db")

    def tearDown(self):
        self.dir.cleanup()

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli.main(["--db", self.db, *argv])
        return code, out.getvalue()

    def test_ingest_pdf_then_match_json(self):
        code, _ = self.run_cli("ingest", str(SAMPLE_PDF))
        self.assertEqual(code, 0)
        code, output = self.run_cli(
            "match", "--skills", "Python,Airflow,PostgreSQL,Power BI", "--top", "2", "--json"
        )
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertEqual(data[0]["ref"], "DEMO 003")
        self.assertEqual(len(data), 2)

    def test_match_on_empty_db_fails(self):
        code, _ = self.run_cli("match", "--skills", "Python")
        self.assertEqual(code, 1)

    def test_search_command(self):
        self.run_cli("ingest", str(SAMPLE_TXT))
        _, output = self.run_cli("search", "kubernetes cluster", "--top", "1")
        self.assertIn("DEMO 006", output)

    def test_export_command(self):
        self.run_cli("ingest", str(SAMPLE_TXT))
        target = os.path.join(self.dir.name, "x.csv")
        code, _ = self.run_cli("export", "--output", target)
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(target))


if __name__ == "__main__":
    unittest.main()
