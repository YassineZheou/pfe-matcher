import unittest

from pfe_matcher.parser import parse_topics
from pfe_matcher.retrieval import TopicIndex
from pfe_matcher.scoring import match_topics
from tests.helpers import SAMPLE_TXT


class ScoringTest(unittest.TestCase):
    def setUp(self):
        self.topics = parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))

    def test_full_coverage_ranks_first(self):
        profile = ["Angular", "Spring Boot", "PostgreSQL", "Power BI", "Docker", "CI/CD"]
        best = match_topics(self.topics, profile, top=3)[0]
        self.assertEqual(best.topic.ref, "DEMO 001")
        self.assertEqual(best.missing, [])
        self.assertEqual(best.coverage, 1.0)

    def test_missing_skills_are_reported(self):
        results = match_topics(self.topics, ["Python", "SQL"], top=8)
        by_ref = {m.topic.ref: m for m in results}
        self.assertIn("LLM", by_ref["DEMO 002"].missing)
        self.assertIn("SQL", by_ref["DEMO 002"].matched)

    def test_score_within_bounds(self):
        for m in match_topics(self.topics, ["Python", "Docker"], top=8):
            self.assertTrue(0 <= m.score <= 100)

    def test_empty_profile_scores_zero(self):
        for m in match_topics(self.topics, [], top=8):
            self.assertEqual(m.score, 0)

    def test_unknown_skills_are_ignored(self):
        self.assertEqual(
            [m.score for m in match_topics(self.topics, ["cobol"], top=8)],
            [0] * 8,
        )

    def test_min_score_filters(self):
        results = match_topics(self.topics, ["Python"], top=8, min_score=50)
        self.assertTrue(all(m.score >= 50 for m in results))

    def test_embedded_profile_matches_sensor_topic(self):
        best = match_topics(self.topics, ["Embarqué", "Python"], top=1)[0]
        self.assertEqual(best.topic.ref, "DEMO 008")

    def test_search_finds_scraping_topic(self):
        found = TopicIndex(self.topics).search("scraping de sites web", top=1)
        self.assertEqual(found[0][0].ref, "DEMO 005")

    def test_search_with_empty_index(self):
        self.assertEqual(TopicIndex([]).search("python"), [])


if __name__ == "__main__":
    unittest.main()
