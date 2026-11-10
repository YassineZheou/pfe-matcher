import os
import tempfile
import unittest

try:
    from fastapi.testclient import TestClient

    from pfe_matcher.api import app

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

from tests.helpers import SAMPLE_PDF


@unittest.skipUnless(HAS_FASTAPI, "fastapi non installé")
class ApiTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        os.environ["PFE_DB"] = os.path.join(self.dir.name, "api.db")
        self.client = TestClient(app)

    def tearDown(self):
        os.environ.pop("PFE_DB", None)
        self.dir.cleanup()

    def upload(self):
        with open(SAMPLE_PDF, "rb") as handle:
            return self.client.post(
                "/topics", files={"file": ("book.pdf", handle, "application/pdf")}
            )

    def test_health(self):
        self.assertEqual(self.client.get("/health").json()["status"], "ok")

    def test_upload_then_match(self):
        self.assertEqual(self.upload().json()["count"], 8)
        response = self.client.get("/match", params={"skills": "Python,Airflow,SQL", "top": 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_match_on_empty_db_is_404(self):
        self.assertEqual(self.client.get("/match", params={"skills": "Python"}).status_code, 404)

    def test_upload_without_topics_is_422(self):
        response = self.client.post(
            "/topics", files={"file": ("x.txt", b"rien", "text/plain")}
        )
        self.assertEqual(response.status_code, 422)

    def test_search(self):
        self.upload()
        response = self.client.get("/search", params={"q": "web scraping"})
        self.assertEqual(response.json()[0]["ref"], "DEMO 005")


if __name__ == "__main__":
    unittest.main()
