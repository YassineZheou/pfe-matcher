import unittest

from pfe_matcher.skills import extract_skills, normalize_skills


class SkillsTest(unittest.TestCase):
    def test_detects_known_skills(self):
        text = "Application Angular et Spring Boot avec PostgreSQL et Docker"
        self.assertEqual(
            extract_skills(text), ["Angular", "Docker", "PostgreSQL", "Spring Boot"]
        )

    def test_java_is_not_javascript(self):
        self.assertEqual(extract_skills("Développement JavaScript"), ["JavaScript"])
        self.assertEqual(extract_skills("Développement Java"), ["Java"])

    def test_sql_not_found_inside_postgresql(self):
        self.assertEqual(extract_skills("base postgresql"), ["PostgreSQL"])

    def test_short_aliases_need_word_boundaries(self):
        self.assertEqual(extract_skills("storage et reactive"), [])

    def test_ci_cd_with_slash(self):
        self.assertIn("CI/CD", extract_skills("pipeline CI/CD"))

    def test_normalize_aliases_and_duplicates(self):
        self.assertEqual(
            normalize_skills(["postgres", "PostgreSQL", " k8s ", "inconnu", ""]),
            ["PostgreSQL", "Kubernetes"],
        )


if __name__ == "__main__":
    unittest.main()
