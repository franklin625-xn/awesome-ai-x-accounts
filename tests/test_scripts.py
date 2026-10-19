"""Regression checks for data validation and deterministic README generation."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_readme import END, START, render_accounts, update_readme
from validate import load_accounts, reject_duplicate_keys, validate_accounts


class SnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accounts = load_accounts()

    def test_actual_snapshot_and_readme(self):
        self.assertEqual(validate_accounts(self.accounts), [])
        text = (ROOT / "docs" / "ORIGINAL_100.md").read_text(encoding="utf-8")
        self.assertEqual(update_readme(text, self.accounts), text)
        rendered = render_accounts(self.accounts)
        self.assertEqual(rendered.count("| #"), 100)
        for account in self.accounts:
            self.assertIn(f'[@{account["handle"]}]({account["url"]})', rendered)
        self.assertEqual(rendered.count('<a id="group-'), 10)

    def test_idempotence_and_manual_text(self):
        text = "manual introduction\n" + START + "\nold\n" + END + "\nmanual footer"
        first = update_readme(text, self.accounts)
        self.assertEqual(update_readme(first, self.accounts), first)
        self.assertTrue(first.startswith("manual introduction\n" + START))
        self.assertTrue(first.endswith(END + "\nmanual footer"))

    def test_invalid_markers(self):
        for text in ("", END + START, START + START + END, START):
            with self.subTest(text=text), self.assertRaises(ValueError):
                update_readme(text, self.accounts)

    def test_invalid_fields(self):
        cases = [("id", True), ("id", 2), ("group_id", True),
                 ("group_id", 2), ("group_id", []), ("language_group", "zh"),
                 ("name", " "), ("focus", None), ("handle", "@sama"),
                 ("url", "https://example.com/sama"), ("source", "other"),
                 ("verified_at", "2026-02-30"), ("verified_at", "9999-01-01"),
                 ("verified_at", True), ("name", "two\nlines")]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                accounts = copy.deepcopy(self.accounts)
                accounts[0][field] = value
                self.assertTrue(validate_accounts(accounts))

    def test_duplicates_missing_and_order(self):
        accounts = copy.deepcopy(self.accounts)
        accounts[1]["handle"] = "SAMA"
        accounts[1]["url"] = "https://x.com/SAMA"
        self.assertTrue(any("重复" in error for error in validate_accounts(accounts)))
        self.assertTrue(validate_accounts(self.accounts[:-1]))
        self.assertTrue(validate_accounts(list(reversed(self.accounts))))
        accounts = copy.deepcopy(self.accounts)
        del accounts[0]["verified_at"]
        self.assertTrue(validate_accounts(accounts))

    def test_malformed_records(self):
        for value in (None, {}, [None] * 100, [{}] * 100):
            self.assertTrue(validate_accounts(value))
        with self.assertRaises(ValueError):
            json.loads('{"id":1,"id":2}', object_pairs_hook=reject_duplicate_keys)

    def test_validator_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            for content in ("[", "[]", '{"id":1}'):
                path.write_text(content, encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "validate.py"),
                     "--data", str(path)], capture_output=True,
                )
                self.assertEqual(result.returncode, 1)
                self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
