import json
import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

PLUGIN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN / "skills/retrieve-relevant-documentation/scripts"))

from repositories import frontmatter
from validate_docs import markdown_content


class PluginTests(unittest.TestCase):
    def test_skills_are_discoverable(self):
        expected = {
            "retrieve-relevant-documentation", "capture-information-in-documentation",
            "verify-documentation-accuracy", "validate-documentation-form", "set-me-up",
        }
        paths = list((PLUGIN / "skills").glob("*/SKILL.md"))
        self.assertEqual({path.parent.name for path in paths}, expected)
        for path in paths:
            with self.subTest(skill=path.parent.name):
                fm = frontmatter(path)
                self.assertEqual(fm["name"], path.parent.name)
                self.assertIsInstance(fm["description"], str)
                self.assertTrue(fm["description"].strip())
                self.assertLessEqual(len(fm["description"]), 1024)

    def test_shared_workflow_references_are_direct(self):
        for name in (
            "capture-information-in-documentation", "verify-documentation-accuracy",
        ):
            text = (PLUGIN / "skills" / name / "SKILL.md").read_text()
            with self.subTest(skill=name):
                self.assertIn("../../reference/proposal-workflow.md", text)
                self.assertIn("../../reference/helpers.md", text)

    def test_plugin_and_marketplace_versions_match(self):
        claude = json.loads((PLUGIN / ".claude-plugin/plugin.json").read_text())
        codex = json.loads((PLUGIN / ".codex-plugin/plugin.json").read_text())
        marketplace = json.loads((PLUGIN.parents[1] / ".claude-plugin/marketplace.json").read_text())
        entry = next(item for item in marketplace["plugins"] if item["name"] == claude["name"])
        self.assertEqual(claude["version"], codex["version"])
        self.assertEqual(claude["version"], entry["version"])
        self.assertTrue((PLUGIN / codex["skills"]).is_dir())
        self.assertEqual((PLUGIN.parents[1] / entry["source"]).resolve(), PLUGIN)

    def test_workflow_reference_links_resolve(self):
        paths = [
            *sorted(PLUGIN.glob("*.md")),
            *sorted((PLUGIN / "reference").glob("*.md")),
            *sorted((PLUGIN / "skills").glob("*/SKILL.md")),
        ]
        for path in paths:
            _, links, _, _ = markdown_content(path.read_text())
            for link in links:
                url = urlsplit(link)
                if url.scheme or url.netloc or not (url.path or url.fragment):
                    continue
                with self.subTest(path=path, link=link):
                    target = path.parent / unquote(url.path) if url.path else path
                    self.assertTrue(target.exists())
                    if url.fragment and target.is_file() and target.suffix == ".md":
                        _, _, anchors, _ = markdown_content(target.read_text())
                        self.assertIn(unquote(url.fragment), anchors)

    def test_documented_helper_paths_resolve(self):
        references = []
        for path in PLUGIN.rglob("*.md"):
            for helper in re.findall(r"skills/[\w/-]+\.py\b", path.read_text()):
                references.append(helper)
                with self.subTest(path=path, helper=helper):
                    self.assertTrue((PLUGIN / helper).is_file())
        self.assertTrue(references)


if __name__ == "__main__":
    unittest.main()
