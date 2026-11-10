import os
import unittest
from unittest import mock

from pfe_matcher.llm import LLMUnavailable, build_prompt, generate_motivation
from pfe_matcher.models import Topic


class LLMTest(unittest.TestCase):
    def setUp(self):
        self.topic = Topic("DEMO 001", "Plateforme web", "texte")

    def test_prompt_contains_only_given_facts(self):
        prompt = build_prompt(self.topic, ["Python"], ["Angular"])
        self.assertIn("Python", prompt)
        self.assertIn("Angular", prompt)
        self.assertIn("n'invente aucune expérience", prompt)

    def test_generate_uses_injected_transport(self):
        captured = {}

        def fake_send(payload, key):
            captured["payload"] = payload
            captured["key"] = key
            return {"choices": [{"message": {"content": "  Bonjour  "}}]}

        text = generate_motivation(
            self.topic, ["Python"], [], api_key="k", send=fake_send
        )
        self.assertEqual(text, "Bonjour")
        self.assertEqual(captured["key"], "k")
        self.assertEqual(captured["payload"]["messages"][0]["role"], "user")

    def test_missing_key_raises(self):
        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaises(LLMUnavailable):
            generate_motivation(self.topic, [], [])


if __name__ == "__main__":
    unittest.main()
