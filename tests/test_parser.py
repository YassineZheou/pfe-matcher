import unittest

from pfe_matcher.parser import parse_topics, read_file
from tests.helpers import SAMPLE_PDF, SAMPLE_TXT


class ParserTest(unittest.TestCase):
    def test_parses_all_sample_topics(self):
        topics = parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))
        self.assertEqual(len(topics), 8)
        self.assertEqual(topics[0].ref, "DEMO 001")

    def test_duration_range_and_single(self):
        topics = {t.ref: t for t in parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))}
        self.assertEqual((topics["DEMO 003"].duration_min, topics["DEMO 003"].duration_max), (4, 6))
        self.assertEqual((topics["DEMO 005"].duration_min, topics["DEMO 005"].duration_max), (4, 4))

    def test_places(self):
        topics = {t.ref: t for t in parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))}
        self.assertEqual(topics["DEMO 001"].places, 2)

    def test_skills_extracted_per_topic(self):
        topics = {t.ref: t for t in parse_topics(SAMPLE_TXT.read_text(encoding="utf-8"))}
        self.assertIn("Angular", topics["DEMO 001"].skills)
        self.assertIn("RAG", topics["DEMO 002"].skills)
        self.assertNotIn("Angular", topics["DEMO 002"].skills)

    def test_duplicate_refs_are_ignored(self):
        text = "AB 001 : Premier\nDurée : 4 mois\nAB 001 : Doublon\nDurée : 6 mois\n"
        topics = parse_topics(text)
        self.assertEqual(len(topics), 1)
        self.assertEqual(topics[0].title, "Premier")

    def test_no_header_gives_no_topic(self):
        self.assertEqual(parse_topics("du texte sans sujet"), [])

    def test_pdf_and_text_give_same_topics(self):
        from_pdf = parse_topics(read_file(SAMPLE_PDF))
        from_txt = parse_topics(read_file(SAMPLE_TXT))
        self.assertEqual([t.ref for t in from_pdf], [t.ref for t in from_txt])
        self.assertEqual([t.skills for t in from_pdf], [t.skills for t in from_txt])


if __name__ == "__main__":
    unittest.main()
