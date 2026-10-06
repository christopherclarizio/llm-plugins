import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "retrieve-relevant-documentation" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_docs
from repositories import DocumentationError


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "repositories.yaml"
        self.config.write_text(
            "repositories:\n  api:\n    remote: https://example.invalid/api.git\n"
            "    authoritative_branch: main\n    local: missing-checkout\n"
            "  types:\n    remote: https://example.invalid/types.git\n"
            "    authoritative_branch: main\n    local: also-missing\n"
        )
        self.code = self.doc("engine", "code", related=["feature"])
        self.product = self.doc("feature", "product", related=["engine"])

    def doc(self, doc_id, directory="code", **fields):
        tree = directory
        fm = {
            "id": doc_id, "title": doc_id.title(), "tree": tree,
            "tier": "subsystem" if tree == "code" else "feature",
            "description": "What this does. Read before changing it.",
            "trust": "agent-generated",
            "code_references": [
                {
                    "repository": name, "paths": ["src/**"],
                    "verified_at": {
                        "commit": "abcdef0123456789", "date": "2026-10-05", "by": "agent",
                    },
                } for name in ("api", "types")
            ],
        }
        fm.update(fields)
        path = self.root / tree / f"{doc_id}.md"
        path.parent.mkdir(exist_ok=True)
        text = "---\n" + yaml.safe_dump(fm) + "---\n"
        for section in validate_docs.SECTIONS[tree]:
            text += f"\n## {section}\n\n"
            text += (
                "Explains the mental model. It does **not** cover deployment.\n"
                if section == "Purpose & scope" else "Useful understanding.\n"
            )
        path.write_text(text)
        return path

    def errors(self):
        return [item for item in validate_docs.validate(self.root, self.config) if not item.warning]

    def assert_error(self, field, text):
        errors = self.errors()
        self.assertTrue(
            any(item.field == field and text in item.message for item in errors),
            errors,
        )

    def test_both_trees_multi_repository_offline_and_read_only(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        with patch("subprocess.run", side_effect=AssertionError("must not access Git")):
            self.assertEqual(validate_docs.validate(self.root, self.config), [])
        self.assertEqual(
            before, {path: path.read_bytes() for path in self.root.rglob("*") if path.is_file()}
        )

    def test_required_fields_and_invalid_types(self):
        for field in ("id", "title", "description", "tree", "tier", "trust"):
            for value in (None, [], {}, 42, ""):
                with self.subTest(field=field, value=value):
                    self.doc("engine", related=["feature"], **{field: value})
                    self.assert_error(field, "non-empty string")

    def test_vocabularies_and_directory(self):
        self.doc("engine", tier="feature", trust="approved", related=["feature"])
        self.assert_error("tier", "expected one of")
        self.assert_error("trust", "must be")
        self.code.write_text(self.code.read_text().replace("tree: code", "tree: product"))
        self.assert_error("tree", "must live under product")

    def test_id_and_duplicates(self):
        self.doc("engine", id="Bad_ID", related=["feature"])
        self.assert_error("id", "kebab-case")
        self.doc("engine", related=["feature"])
        self.doc("copy", id="engine")
        self.assert_error("id", "duplicate")

    def test_navigation_types_and_duplicates(self):
        for field in ("children", "related", "keywords"):
            for value in ("wrong", [None], ["x", "x"]):
                with self.subTest(field=field, value=value):
                    self.doc("engine", **{field: value})
                    self.assertTrue(any(item.field == field for item in self.errors()))
        self.doc("engine", parent=[])
        self.assert_error("parent", "document ID")

    def test_unknown_repositories_and_invalid_metadata(self):
        original = self.code.read_text()
        for old, new, message in (
            ("repository: api", "repository: unknown", "unknown repository"),
            ("src/**", "../outside", "repo-relative"),
            ("src/**", "C:/outside", "repo-relative"),
            ("abcdef0123456789", "main", "Git commit SHA"),
            ("2026-10-05", "2026-99-99", "YYYY-MM-DD"),
            ("by: agent", "by: null", "non-empty string"),
        ):
            with self.subTest(new=new):
                self.code.write_text(original.replace(old, new))
                self.assert_error("code_references", message)

    def test_duplicate_yaml_and_missing_frontmatter(self):
        self.code.write_text("---\nid: engine\nid: duplicate\n---\n")
        self.assert_error("frontmatter", "duplicate YAML key")
        self.code.write_text("no metadata")
        self.assert_error("frontmatter", "missing opening")

    def test_missing_references_and_unknown_fields_are_explicit_errors(self):
        text = self.code.read_text()
        self.code.write_text(text.replace("code_references:", "references:"))
        self.assert_error("code_references", "non-empty list")
        self.assert_error("references", "unknown frontmatter field")

    def test_hierarchy_resolves_and_is_reciprocal(self):
        self.doc("system", tier="architecture", children=["engine"])
        self.doc("engine", parent="system", related=["feature"])
        self.assertEqual(self.errors(), [])
        self.doc("engine", parent="missing", related=["feature"])
        self.assert_error("parent", "unresolved")
        self.assert_error("children", "must name")
        self.doc("engine", parent="feature", related=["feature"])
        self.assert_error("parent", "within one tree")
        self.doc("engine", children=["engine"])
        self.assert_error("children", "itself")

    def test_hierarchy_altitude_and_cycles_rejected(self):
        self.doc("component", tier="component", parent="engine", children=["engine"])
        self.doc("engine", parent="component", children=["component"])
        self.assert_error("parent", "coarser")
        self.assert_error("children", "finer")

    def test_body_sections_and_scope(self):
        original = self.code.read_text()
        self.code.write_text(original.replace("## Concept\n\nUseful understanding.", "## Concept"))
        self.assert_error("body", "empty section: Concept")
        self.code.write_text(original.replace("## Concept", "## Different heading"))
        self.assert_error("body", "missing or empty section: Concept")
        self.code.write_text(original.replace("It does **not** cover deployment.", "It covers everything."))
        self.assert_error("Purpose & scope", "state explicitly")
        self.code.write_text(original.replace("Useful understanding.", "<stable-kebab-slug>", 1))
        self.assert_error("body", "placeholder")

    def test_scope_exclusions_can_wrap_across_lines(self):
        self.code.write_text(self.code.read_text().replace("does **not** cover", "does\n**not** cover"))
        self.assertEqual(self.errors(), [])

    def test_inline_reference_image_html_links_and_anchors(self):
        (self.root / "diagram.svg").write_text("<svg/>")
        with self.code.open("a") as file:
            file.write(
                "\n[feature](../product/feature.md#what-it-is)\n"
                "[scope][scope-ref]\n\n[scope-ref]: #purpose--scope\n"
                "![diagram](../diagram.svg)\n"
                '<a href="../product/feature.md#how-it-is-used">bad</a>\n'
            )
        self.assert_error("link", "missing heading/anchor")
        self.code.write_text(self.code.read_text().replace("#how-it-is-used", "#how-its-used"))
        self.assertEqual(self.errors(), [])
        with self.code.open("a") as file:
            file.write("\n[missing](absent.md)\n![missing](absent.png)\n")
        self.assertEqual(sum(item.field == "link" for item in self.errors()), 2)

    def test_link_parsing_titles_escapes_fences_and_duplicate_headings(self):
        with self.product.open("a") as file:
            file.write('\n## Extra\n\nOne.\n\n## Extra\n\nTwo.\n\n<a id="custom"></a>\n')
        with self.code.open("a") as file:
            file.write(
                '\n[title](../product/feature.md#extra-1 "description")\n'
                '[custom](../product/feature.md#custom)\n'
                '\\[escaped](absent.md)\n'
                '```\n[not a link](absent.md)\n```\n'
                '[external](https://example.invalid/missing)\n'
            )
        self.assertEqual(self.errors(), [])

    def test_percent_encoded_link(self):
        (self.root / "space name.txt").write_text("exists")
        with self.code.open("a") as file:
            file.write("\n[text](../space%20name.txt)\n")
        self.assertEqual(self.errors(), [])
        with self.code.open("a") as file:
            file.write("\n[absolute](%2Foutside.md)\n")
        self.assert_error("link", "relative path")

    def test_directory_links_resolve(self):
        with self.code.open("a") as file:
            file.write("\n[directory](../product/)\n")
        self.assertEqual(self.errors(), [])

    def test_html_links_reject_unsupported_schemes(self):
        with self.code.open("a") as file:
            file.write('\n<a href="file:///etc/example">unsupported</a>\n')
        self.assert_error("link", "supported URL")

    def test_altitude_warning_threshold(self):
        original = self.code.read_text()
        for lines, warnings in ((20, 0), (21, 1)):
            with self.subTest(lines=lines):
                self.code.write_text(original + "\n```\n" + "code\n" * lines + "```\n")
                diagnostics = validate_docs.validate(self.root, self.config)
                self.assertEqual(sum(item.field == "altitude" for item in diagnostics), warnings)

    def test_warnings_and_strict_cli(self):
        self.doc("engine")
        with self.code.open("a") as file:
            file.write("\n```python\n" + "print('trivia')\n" * 21 + "```\n")
        diagnostics = validate_docs.validate(self.root, self.config)
        self.assertEqual(sum(item.warning for item in diagnostics), 2)
        for args, expected in (([], 0), (["--strict"], 1)):
            output = io.StringIO()
            with patch.object(sys, "argv", [
                "validate_docs.py", "--corpus-root", str(self.root), *args,
            ]), contextlib.redirect_stdout(output):
                self.assertEqual(validate_docs.main(), expected)
            self.assertIn("WARNING:", output.getvalue())

    def test_configuration_and_empty_corpus_errors(self):
        with self.assertRaises(DocumentationError):
            validate_docs.validate(self.root, self.root / "missing.yaml")
        self.code.unlink()
        self.product.unlink()
        with self.assertRaisesRegex(DocumentationError, "no documents"):
            validate_docs.validate(self.root, self.config)

    def test_read_failure_reports_error_without_traceback(self):
        output = io.StringIO()
        with patch.object(sys, "argv", [
            "validate_docs.py", "--corpus-root", str(self.root),
        ]), patch.object(validate_docs, "read_text", side_effect=DocumentationError("cannot read")), \
                contextlib.redirect_stderr(output):
            self.assertEqual(validate_docs.main(), 2)
        self.assertIn("cannot read", output.getvalue())

    def test_real_cli_invalid_document_and_missing_registry(self):
        before = self.code.read_bytes()
        command = [sys.executable, str(SCRIPTS / "validate_docs.py"), "--corpus-root", str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(before, self.code.read_bytes())
        self.code.write_text("broken")
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertIn("frontmatter", result.stdout)
        self.config.unlink()
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr + result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_bundled_corpus_validates(self):
        plugin = SCRIPTS.parents[2]
        self.assertEqual(
            validate_docs.validate(plugin / "examples", plugin / "examples/repositories.example.yaml"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
