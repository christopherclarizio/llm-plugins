import ast
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "skills/retrieve-relevant-documentation/scripts"
DEPENDENCIES = {
    "discover_docs.py": ["PyYAML>=6.0.2,<7"],
    "check_staleness.py": ["PyYAML>=6.0.2,<7"],
    "refresh_repositories.py": ["PyYAML>=6.0.2,<7"],
    "validate_docs.py": ["PyYAML>=6.0.2,<7", "markdown-it-py>=3,<4"],
}


class UvTests(unittest.TestCase):
    def test_executable_helpers_declare_dependencies_and_ship_locks(self):
        for name, dependencies in DEPENDENCIES.items():
            with self.subTest(script=name):
                script = SCRIPTS / name
                text = script.read_text()
                self.assertTrue(text.startswith("#!/usr/bin/env -S uv run --locked --script\n"))
                self.assertIn('# requires-python = ">=3.9"\n', text)
                metadata = re.search(r"# /// script\n(.*?)# ///\n", text, re.S)
                self.assertIsNotNone(metadata)
                declared = re.search(r"^# dependencies = (.+)$", metadata[1], re.M)
                self.assertIsNotNone(declared)
                self.assertEqual(ast.literal_eval(declared[1]), dependencies)
                self.assertTrue(script.with_suffix(".py.lock").is_file())

    def test_setup_skill_covers_installation_and_persistent_configuration(self):
        skill = (PLUGIN / "skills/set-me-up/SKILL.md").read_text()
        references = ("setup-unix.md", "setup-windows.md", "helpers.md")
        for name in references:
            with self.subTest(reference=name):
                self.assertIn(f"../../reference/{name}", skill)
        text = skill + "\n".join(
            (PLUGIN / "reference" / name).read_text() for name in references
        )
        for required in (
            "command -v uv", "command -v git", "uv --version", "git --version",
            "brew install uv", "brew install git", "astral.sh/uv/install.sh",
            "NMWS_DOCS_CORPUS_ROOT", ".zshenv", ".bashrc",
            "SetEnvironmentVariable", "'User'", "parent agent",
        ):
            with self.subTest(required=required):
                self.assertIn(required, text)

    @unittest.skipUnless(shutil.which("uv"), "uv is required for script integration checks")
    def test_helpers_run_isolated_from_an_unrelated_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "unrelated"\nversion = "0.0.0"\n'
                'requires-python = ">=99"\n'
                'dependencies = ["nmws-nonexistent-dependency"]\n'
            )
            before = {path.name: path.read_bytes() for path in root.iterdir()}
            for name in DEPENDENCIES:
                with self.subTest(script=name):
                    result = subprocess.run(
                        ["uv", "run", "--locked", "--script", str(SCRIPTS / name), "--help"],
                        cwd=root, capture_output=True, text=True, timeout=120,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("usage:", result.stdout)
            result = subprocess.run(
                [
                    "uv", "run", "--locked", "--script", str(SCRIPTS / "validate_docs.py"),
                    "--corpus-root", str(PLUGIN / "examples"),
                    "--registry", str(PLUGIN / "examples/repositories.example.yaml"),
                ],
                cwd=root, capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("VALIDATION: 0 error(s), 0 warning(s)", result.stdout)
            self.assertEqual(
                before, {path.name: path.read_bytes() for path in root.iterdir()}
            )


if __name__ == "__main__":
    unittest.main()
