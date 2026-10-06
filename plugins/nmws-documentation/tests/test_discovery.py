import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/retrieve-relevant-documentation/scripts"
sys.path.insert(0, str(SCRIPTS))

import discover_docs
from repositories import DocumentationError, frontmatter


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def doc(self, doc_id, tree="code", tier="component", body="", **fields):
        fm = {
            "id": doc_id, "title": doc_id.replace("-", " ").title(), "tree": tree,
            "tier": tier, "description": "Playback frame cache behavior.",
            "keywords": ["playback"], "trust": "draft",
            "code_references": [{
                "repository": "missing-checkout", "paths": ["src/**"],
                "verified_at": {"commit": "0000000", "date": "2026-10-05", "by": "agent"},
            }],
        }
        fm.update(fields)
        path = self.root / tree / f"{doc_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\n" + yaml.safe_dump(fm) + "---\n" + body, encoding="utf-8")
        return path

    def run_helper(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", [
            "discover_docs.py", "--corpus-root", str(self.root), *args,
        ]), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = discover_docs.main()
        return code, json.loads(out.getvalue()), err.getvalue()

    def test_focused_exact_component_and_orientation_coarse(self):
        self.doc("playback", tier="architecture")
        self.doc("frame-cache", keywords=["frame cache"])
        self.doc("unrelated", description="Account creation.", keywords=["account"])
        focused = discover_docs.discover(self.root, "frame cache")
        self.assertEqual([doc["id"] for doc in focused["candidates"]], ["frame-cache", "playback"])
        self.assertIn("keywords", focused["candidates"][0]["match"]["exact_fields"])
        orientation = discover_docs.discover(self.root, "frame cache", mode="orientation")
        self.assertEqual(orientation["candidates"][0]["id"], "playback")
        self.assertEqual(orientation["matched"], 2)

    def test_exact_id_then_title_then_keyword_and_relevance_before_altitude(self):
        self.doc("cache", title="Other", description="Other.", keywords=[])
        self.doc("titled", tier="architecture", title="Cache", keywords=[])
        self.doc("keyword", keywords=["cache"])
        self.doc("partial", title="A Cache Component", keywords=[])
        candidates = discover_docs.discover(self.root, "cache")["candidates"]
        self.assertEqual(
            [doc["id"] for doc in candidates], ["cache", "titled", "keyword", "partial"],
        )
        self.doc("overview", tier="architecture", description="Playback.", keywords=[])
        self.doc("detail", description="Playback frame cache.", keywords=[])
        result = discover_docs.discover(self.root, "playback frame")
        self.assertLess(
            [doc["id"] for doc in result["candidates"]].index("detail"),
            [doc["id"] for doc in result["candidates"]].index("overview"),
        )

    def test_case_punctuation_and_multiline_yaml(self):
        path = self.doc("cache", keywords=["frame cache"])
        path.write_text(path.read_text().replace(
            "description: Playback frame cache behavior.",
            "description: >\n  Playback frame cache\n  behavior.",
        ))
        result = discover_docs.discover(self.root, "FRAME-cache?")
        self.assertEqual(result["candidates"][0]["match"]["exact_fields"], ["keywords"])
        self.assertEqual(result["candidates"][0]["description"], "Playback frame cache behavior.\n")

    def test_product_orientation_and_tree_filter(self):
        self.doc("code", tier="architecture")
        self.doc("product", tree="product", tier="overview")
        self.doc("workflow", tree="product", tier="workflow")
        result = discover_docs.discover(self.root, "playback", mode="orientation", tree="product")
        self.assertEqual([doc["id"] for doc in result["candidates"]], ["product", "workflow"])
        self.assertEqual(result["scanned"], 3)

    def test_default_limit_hard_limit_and_stable_ties(self):
        for number in reversed(range(30)):
            self.doc(f"doc-{number:02}")
        result = discover_docs.discover(self.root, "playback")
        self.assertEqual(len(result["candidates"]), 5)
        self.assertEqual(result["matched"], 30)
        self.assertTrue(result["truncated"])
        self.assertEqual(
            [doc["id"] for doc in result["candidates"]],
            [f"doc-{number:02}" for number in range(5)],
        )
        self.assertEqual(len(discover_docs.discover(self.root, "playback", limit=20)["candidates"]), 20)
        for limit in (0, -1, 21):
            with self.subTest(limit=limit), self.assertRaises(DocumentationError):
                discover_docs.discover(self.root, "playback", limit=limit)

    def test_id_navigation_and_empty_matches_are_successful_json(self):
        self.doc("parent", tier="architecture", children=["child"], related=["feature"])
        self.doc("child", parent="parent")
        self.doc("feature", tree="product", tier="feature")
        code, result, err = self.run_helper("--id", "parent")
        self.assertEqual((code, err), (0, ""))
        candidate = result["candidates"][0]
        self.assertEqual(candidate["children"], ["child"])
        self.assertEqual(candidate["related"], ["feature"])
        self.assertEqual(candidate["path"], "code/parent.md")
        self.assertEqual(candidate["trust"], "draft")
        self.assertNotIn("code_references", candidate)
        self.assertNotIn("freshness", candidate)
        for args in (("--query", "absent"), ("--id", "missing")):
            code, result, err = self.run_helper(*args)
            self.assertEqual((code, result["candidates"], err), (0, [], ""))
            self.assertFalse(result["truncated"])

    def test_query_free_orientation_and_invalid_queries(self):
        self.doc("detail")
        self.doc("overview", tier="architecture")
        result = discover_docs.discover(self.root, mode="orientation")
        self.assertEqual(result["candidates"][0]["id"], "overview")
        for query in ("", "  ", "how is it", "???"):
            with self.subTest(query=query), self.assertRaises(DocumentationError):
                discover_docs.discover(self.root, query)

    def test_only_frontmatter_read_no_git_or_writes(self):
        path = self.doc("cache", body="BODY_MARKER\n" * 10000)
        before = path.read_bytes()
        original_open = Path.open
        lines = []

        class HeaderOnly:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                self.stream.__enter__()
                return self

            def __exit__(self, *args):
                return self.stream.__exit__(*args)

            def readline(self):
                line = self.stream.readline()
                self.assert_header(line)
                return line

            def assert_header(self, line):
                if lines.count(b"---\n") == 2:
                    raise AssertionError("read beyond closing frontmatter")
                lines.append(line)

            def __iter__(self):
                return self

            def __next__(self):
                line = self.readline()
                if not line:
                    raise StopIteration
                return line

        def open_header(target, *args, **kwargs):
            self.assertEqual(args, ("rb",))
            return HeaderOnly(original_open(target, *args, **kwargs))

        with patch.object(Path, "open", open_header), patch(
            "subprocess.run", side_effect=AssertionError("must not access Git"),
        ):
            result = discover_docs.discover(self.root, "cache")
        self.assertNotIn("BODY_MARKER", json.dumps(result))
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(sorted(self.root.rglob("*.md")), [path])
        path.write_bytes(before.split(b"---\n", 2)[0] + b"---\nid: binary-body\n---\n\xff")
        self.assertEqual(frontmatter(path), {"id": "binary-body"})

    def test_errors_are_explicit_json_without_partial_success(self):
        self.doc("valid")
        invalid = self.doc("bad")
        original = invalid.read_text()
        for text in (
            "no frontmatter", "---\nid: bad\n", "---\nid: [\n---\n",
            original.replace("id: bad", "id: bad\nid: duplicate"),
            original.replace("keywords:\n- playback", "keywords: wrong"),
            original.replace("tier: component", "tier: workflow"),
            original.replace("trust: draft", "trust: approved"),
        ):
            with self.subTest(text=text):
                invalid.write_text(text)
                code, result, err = self.run_helper("--query", "playback")
                self.assertEqual(code, 2)
                self.assertEqual(result["candidates"], [])
                self.assertTrue(result["error"])
                self.assertIn("error:", err)
        invalid.write_text(original.replace("id: bad", "id: valid"))
        with self.assertRaisesRegex(DocumentationError, "duplicate ID"):
            discover_docs.discover(self.root, "playback")

    def test_empty_missing_corpus_and_unreadable_header(self):
        with self.assertRaisesRegex(DocumentationError, "no documents"):
            discover_docs.discover(self.root, "playback")
        with self.assertRaisesRegex(DocumentationError, "not a directory"):
            discover_docs.discover(self.root / "missing", "playback")
        path = self.doc("cache")
        path.write_bytes(b"---\nid: \xff\n---\n")
        with self.assertRaises(DocumentationError):
            discover_docs.discover(self.root, "playback")
        with patch.object(Path, "open", side_effect=OSError("denied")):
            with self.assertRaisesRegex(DocumentationError, "denied"):
                discover_docs.discover(self.root, "playback")


if __name__ == "__main__":
    unittest.main()
