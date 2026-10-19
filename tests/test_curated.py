"""Offline regression checks for selection mapping and honest evidence states."""

import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_curated import render_curated, render_research, replace_block
from generate_readme import escape_cell
from validate_curated import load_curated, validate_curated, valid_url


class CuratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accounts, cls.original, cls.research = load_curated()

    def test_actual_selection(self):
        self.assertEqual(validate_curated(self.accounts, self.original, self.research), [])
        self.assertEqual(len(self.accounts), 80)
        selected = {a["original_id"] for a in self.accounts}
        self.assertEqual(len(set(range(1, 101)) - selected), 20)
        rendered = render_curated(self.accounts)
        self.assertEqual(rendered.count("[@"), 80)
        self.assertNotIn("待核验", rendered)
        self.assertNotIn("（原 #", rendered)
        self.assertEqual(render_research(self.accounts, self.original, self.research).count("#### 原 #"), 100)

    def test_documents_consistent_and_idempotent(self):
        docs = [("README.md", "CURATED", render_curated(self.accounts)),
                ("docs/RESEARCH.md", "RESEARCH", render_research(self.accounts, self.original, self.research))]
        for path, marker, content in docs:
            text = (ROOT / path).read_text(encoding="utf-8")
            start, end = f"<!-- {marker}:START -->", f"<!-- {marker}:END -->"
            self.assertEqual(replace_block(text, start, end, content), text)
            first = replace_block("manual\n" + start + "old" + end + "\nfooter", start, end, content)
            self.assertEqual(replace_block(first, start, end, content), first)
            self.assertTrue(first.startswith("manual\n"))
            self.assertTrue(first.endswith("\nfooter"))

    def test_markers_and_escaping(self):
        for text in ("", "ENDSTART", "STARTSTARTEND"):
            with self.assertRaises(ValueError):
                replace_block(text, "START", "END", "content")
        escaped = escape_cell("[name]|<tag>_star*")
        self.assertIn("&#124;", escaped)
        self.assertIn("\\[name\\]", escaped)
        self.assertIn("\\<tag\\>", escaped)
        self.assertNotIn("|", escaped)

    def test_bad_selection(self):
        for field, value in [("original_id", True), ("original_id", []),
                             ("category", True), ("name", "Other"),
                             ("order", 0), ("evidence_status", []),
                             ("evidence_urls", []), ("research_date", "9999-01-01"),
                             ("verified_at", "2026-10-19")]:
            accounts = copy.deepcopy(self.accounts)
            accounts[0][field] = value
            with self.subTest(field=field):
                self.assertTrue(validate_curated(accounts, self.original, self.research))
        self.assertTrue(validate_curated(self.accounts[:-1], self.original, self.research))
        accounts = copy.deepcopy(self.accounts)
        accounts[-1] = copy.deepcopy(accounts[0])
        self.assertTrue(validate_curated(accounts, self.original, self.research))

    def test_bad_research(self):
        for research in (None, {}, {"records": []}):
            self.assertTrue(validate_curated(self.accounts, self.original, research))
        for field, value in [("id", True), ("status", []), ("sources", ["http://bad"]),
                             ("advantage", None), ("attempts", None)]:
            research = copy.deepcopy(self.research)
            research["records"][0][field] = value
            with self.subTest(field=field):
                self.assertTrue(validate_curated(self.accounts, self.original, research))
        research = copy.deepcopy(self.research)
        research["records"][-1] = copy.deepcopy(research["records"][0])
        self.assertTrue(validate_curated(self.accounts, self.original, research))

    def test_pending_not_invented(self):
        for account in self.accounts:
            if account["evidence_status"] == "pending":
                self.assertIsNone(account["advantage"])
                self.assertEqual(account["evidence_urls"], [])
            self.assertIsNone(account["verified_at"])
        for url in ("javascript:alert(1)", "http://example.com", "https://x.com/a b", "https://[", None):
            self.assertFalse(valid_url(url))


if __name__ == "__main__":
    unittest.main()
