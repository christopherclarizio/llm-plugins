import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "docs-router" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import check_staleness
import refresh_repositories
from repositories import DocumentationError, code_references, refresh, registry


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.config = self.root / "repositories.yaml"
        self.configured = {}
        self.git_env = {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.invalid",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
        }
        self.env_patch = patch.dict("os.environ", self.git_env)
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)

    def git(self, path, *args):
        return subprocess.run(
            ["git", "-C", str(path), *args], check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def make_repo(self, name):
        remote = self.root / f"{name}.git"
        writer = self.root / f"{name}-writer"
        local = self.root / f"{name}-local"
        self.git(self.root, "init", "--bare", "--initial-branch=main", str(remote))
        self.git(self.root, "clone", str(remote), str(writer))
        (writer / "src").mkdir()
        (writer / "src" / "api.txt").write_text("initial\n")
        self.git(writer, "add", ".")
        self.git(writer, "commit", "-m", "initial")
        initial = self.git(writer, "rev-parse", "HEAD")
        self.git(writer, "push", "origin", "main")
        self.git(self.root, "clone", str(remote), str(local))
        self.configured[name] = (remote, writer, local, initial)
        self.write_registry()
        return self.configured[name]

    def write_registry(self):
        text = "repositories:\n"
        for name, (remote, _, local, _) in self.configured.items():
            text += (
                f"  {name}:\n    remote: {remote}\n"
                f"    authoritative_branch: main\n    local: {local.name}\n"
            )
        self.config.write_text(text)

    def commit(self, path, filename="src/api.txt", push=True):
        file = path / filename
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(file.read_text() + "changed\n" if file.exists() else "changed\n")
        self.git(path, "add", ".")
        self.git(path, "commit", "-m", "change")
        sha = self.git(path, "rev-parse", "HEAD")
        if push:
            self.git(path, "push", "origin", "main")
        return sha

    def doc(self, names, filename="doc.md"):
        text = "---\nid: test\ntrust: draft\ncode_references:\n"
        for name in names:
            paths = "src/**, config/allowlist/**" if name == "gateway" else "src/**"
            text += (
                f"  - repository: {name}\n    paths: [{paths}]\n    verified_at:\n"
                f"      commit: '{self.configured[name][3]}'\n"
                "      date: 2026-10-05\n      by: agent\n"
            )
        path = self.root / filename
        path.write_text(text + "---\n\nIllustrative documentation.\n")
        return path

    def run_checker(self, *args):
        output = io.StringIO()
        with patch.object(sys, "argv", ["check_staleness.py", *map(str, args)]):
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                code = check_staleness.main()
        return code, output.getvalue()

    def assert_refresh_fails_unchanged(self, name, message):
        repo = registry(self.config)[name]
        before = self.git(repo.local, "rev-parse", "HEAD")
        status = self.git(repo.local, "status", "--porcelain")
        with self.assertRaisesRegex(DocumentationError, message):
            refresh(repo)
        self.assertEqual(before, self.git(repo.local, "rev-parse", "HEAD"))
        self.assertEqual(status, self.git(repo.local, "status", "--porcelain"))

    def test_multi_repo_gateway_drift(self):
        for name in ("napi", "types", "gateway"):
            self.make_repo(name)
        doc = self.doc(["napi", "types", "gateway"])
        target = self.commit(self.configured["gateway"][1], "config/allowlist/api.txt")
        code, output = self.run_checker(doc, "--registry", self.config)
        self.assertEqual(code, 1, output)
        self.assertIn(f"OK: {doc} [napi]", output)
        self.assertIn(f"OK: {doc} [types]", output)
        self.assertIn(f"STALE: {doc} [gateway]", output)
        self.assertIn("stale", output)
        self.assertEqual(target, self.git(self.configured["gateway"][2], "rev-parse", "HEAD"))
        self.assertEqual(
            (self.configured["gateway"][1] / "config/allowlist/api.txt").read_text(),
            (self.configured["gateway"][2] / "config/allowlist/api.txt").read_text(),
        )

    def test_fresh_and_idempotent_refresh(self):
        _, _, local, initial = self.make_repo("napi")
        doc = self.doc(["napi"])
        for _ in range(2):
            code, output = self.run_checker(doc, "--registry", self.config)
            self.assertEqual(code, 0, output)
            self.assertIn(initial, output)
        self.assertEqual(initial, self.git(local, "rev-parse", "HEAD"))

    def test_unrelated_upstream_change_keeps_doc_fresh(self):
        _, writer, local, _ = self.make_repo("napi")
        target = self.commit(writer, "README.md")
        code, output = self.run_checker(self.doc(["napi"]), "--registry", self.config)
        self.assertEqual(code, 0, output)
        self.assertEqual(target, self.git(local, "rev-parse", "HEAD"))

    def test_refresh_once_for_multiple_docs(self):
        self.make_repo("napi")
        docs = [self.doc(["napi"], name) for name in ("a.md", "b.md")]
        with patch.object(check_staleness, "refresh", wraps=refresh) as refreshing:
            code, output = self.run_checker(*docs, "--registry", self.config)
        self.assertEqual(code, 0, output)
        self.assertEqual(refreshing.call_count, 1)

    def test_dirty_tracked_and_untracked_checkouts(self):
        _, _, local, _ = self.make_repo("napi")
        (local / "src/api.txt").write_text("developer edit\n")
        self.assert_refresh_fails_unchanged("napi", "dirty")
        self.git(local, "add", ".")
        self.assert_refresh_fails_unchanged("napi", "dirty")
        self.git(local, "commit", "-m", "developer edit")
        (local / "untracked.txt").write_text("keep me")
        self.assert_refresh_fails_unchanged("napi", "dirty")

    def test_wrong_branch_and_detached_head(self):
        _, _, local, initial = self.make_repo("napi")
        self.git(local, "switch", "-c", "feature")
        self.assert_refresh_fails_unchanged("napi", "expected branch main")
        self.git(local, "switch", "--detach", initial)
        self.assert_refresh_fails_unchanged("napi", "symbolic-ref")

    def test_local_only_commits(self):
        _, _, local, _ = self.make_repo("napi")
        self.commit(local, push=False)
        self.assert_refresh_fails_unchanged("napi", "local-only or divergent")

    def test_divergent_commits(self):
        _, writer, local, _ = self.make_repo("napi")
        self.commit(local, "local.txt", push=False)
        self.commit(writer, "remote.txt")
        self.assert_refresh_fails_unchanged("napi", "local-only or divergent")

    def test_mismatched_remote(self):
        self.make_repo("napi")
        self.config.write_text(self.config.read_text().replace("napi.git", "wrong.git"))
        self.assert_refresh_fails_unchanged("napi", "remote does not match")

    def test_failed_fetch_is_incomplete(self):
        remote, _, local, initial = self.make_repo("napi")
        remote.rename(self.root / "unavailable.git")
        code, output = self.run_checker(self.doc(["napi"]), "--registry", self.config)
        self.assertEqual(code, 2, output)
        self.assertIn("not confirmed current", output)
        self.assertIn("incomplete", output)
        self.assertEqual(initial, self.git(local, "rev-parse", "HEAD"))

    def test_error_does_not_hide_other_stale_references(self):
        self.make_repo("napi")
        _, writer, _, _ = self.make_repo("gateway")
        self.commit(writer)
        self.config.write_text(self.config.read_text().replace("napi-local", "missing-local"))
        code, output = self.run_checker(self.doc(["napi", "gateway"]), "--registry", self.config)
        self.assertEqual(code, 2, output)
        self.assertIn("[gateway]", output)
        self.assertIn("STALE:", output)
        self.assertIn("incomplete", output)

    def test_unknown_repository(self):
        self.make_repo("napi")
        doc = self.doc(["napi"])
        doc.write_text(doc.read_text().replace("repository: napi", "repository: absent"))
        code, output = self.run_checker(doc, "--registry", self.config)
        self.assertEqual(code, 2, output)
        self.assertIn("unknown repository ID", output)

    def test_missing_and_nonancestor_verification_commits(self):
        _, writer, local, _ = self.make_repo("napi")
        doc = self.doc(["napi"])
        original = doc.read_text()
        doc.write_text(original.replace(self.configured["napi"][3], "f" * 40))
        code, output = self.run_checker(doc, "--registry", self.config)
        self.assertEqual(code, 2, output)
        self.git(local, "switch", "-c", "other")
        other = self.commit(local, "other.txt", push=False)
        self.git(local, "switch", "main")
        doc.write_text(original.replace(self.configured["napi"][3], other))
        code, output = self.run_checker(doc, "--registry", self.config)
        self.assertEqual(code, 2, output)
        self.assertIn("not an ancestor", output)

    def test_override_paths_resolve_against_override_file(self):
        self.make_repo("napi")
        folder = self.root / "developer"
        folder.mkdir()
        override = folder / "local.yaml"
        override.write_text("repositories:\n  napi:\n    local: ../napi-local\n")
        self.assertEqual(registry(self.config, override)["napi"].local, self.root / "napi-local")
        code, output = self.run_checker(
            self.doc(["napi"]), "--registry", self.config, "--override", override
        )
        self.assertEqual(code, 0, output)

    def test_override_cannot_change_repository_identity(self):
        self.make_repo("napi")
        override = self.root / "local.yaml"
        override.write_text("repositories:\n  napi:\n    remote: elsewhere\n")
        with self.assertRaisesRegex(DocumentationError, "only set local"):
            registry(self.config, override)
        override.write_text("repositories:\n  missing:\n    local: elsewhere\n")
        with self.assertRaisesRegex(DocumentationError, "unknown repository"):
            registry(self.config, override)

    def test_registry_validation(self):
        invalid = [
            "repositories: []",
            "repositories:\n  a:\n    local: .",
            "repositories:\n  a: wrong",
            "repositories:\n  a: {}\n  a: {}",
            "repositories:\n  42: {}",
            "repositories: [",
        ]
        for text in invalid:
            with self.subTest(text=text):
                self.config.write_text(text)
                with self.assertRaises(DocumentationError):
                    registry(self.config)

    def test_invalid_frontmatter(self):
        self.make_repo("napi")
        valid = self.doc(["napi"]).read_text()
        invalid = [
            "no frontmatter",
            "---\nunclosed",
            "---\ncode_references: []\n---",
            valid.replace("code_references:", "sources: [src/**]\ncode_references:"),
            valid.replace("code_references:", "verified_at: {}\ncode_references:"),
            valid.replace("paths: [src/**]", "paths: []"),
            valid.replace("paths: [src/**]", "paths: [../outside]"),
            valid.replace("paths: [src/**]", "paths: [':(top)*']"),
            valid.replace("date: 2026-10-05", "date: not-a-date"),
            valid.replace("date: 2026-10-05", "date: 2026-99-99"),
            valid.replace("date: 2026-10-05", "date: '20261005'"),
            valid.replace("by: agent", "by: null"),
            valid.replace(f"commit: '{self.configured['napi'][3]}'", "commit: main"),
        ]
        doc = self.root / "invalid.md"
        for text in invalid:
            with self.subTest(text=text):
                doc.write_text(text)
                with self.assertRaises(DocumentationError):
                    code_references(doc)

    def test_legacy_block_and_inline_sources(self):
        _, writer, local, initial = self.make_repo("napi")
        doc = self.root / "legacy.md"
        for sources in ("sources:\n  - src/**", "sources: [src/**]"):
            doc.write_text(f"---\n{sources}\nverified_at:\n  commit: '{initial}'\n---\n")
            code, output = self.run_checker(doc, "--repo", local)
            self.assertEqual(code, 0, output)
            self.assertIn("upstream not checked", output)
        target = self.commit(writer)
        self.git(local, "fetch", "origin", "main")
        self.git(local, "merge", "--ff-only", target)
        code, output = self.run_checker(doc, "--repo", local)
        self.assertEqual(code, 1, output)

    def test_legacy_working_tree_changes(self):
        _, _, local, initial = self.make_repo("napi")
        doc = self.root / "legacy.md"
        doc.write_text(f"---\nsources: [src/**]\nverified_at:\n  commit: '{initial}'\n---\n")
        (local / "src/new.txt").write_text("untracked")
        code, output = self.run_checker(doc, "--repo", local)
        self.assertEqual(code, 1, output)
        self.assertIn("Uncommitted", output)

    def test_linked_worktree_supported(self):
        _, writer, local, initial = self.make_repo("napi")
        self.git(local, "switch", "-c", "feature")
        linked = self.root / "linked"
        self.git(local, "worktree", "add", str(linked), "main")
        self.config.write_text(self.config.read_text().replace("napi-local", "linked"))
        target = self.commit(writer)
        code, output = self.run_checker(self.doc(["napi"]), "--registry", self.config)
        self.assertEqual(code, 1, output)
        self.assertEqual(target, self.git(linked, "rev-parse", "HEAD"))
        self.assertEqual(initial, self.git(local, "rev-parse", "HEAD"))
        self.assertEqual("feature", self.git(local, "branch", "--show-current"))

    def test_checkout_subdirectory_rejected(self):
        self.make_repo("napi")
        self.config.write_text(self.config.read_text().replace("napi-local", "napi-local/src"))
        with self.assertRaisesRegex(DocumentationError, "checkout root"):
            refresh(registry(self.config)["napi"])

    def test_standalone_refresh_helper(self):
        self.make_repo("napi")
        output = io.StringIO()
        with patch.object(sys, "argv", [
            "refresh_repositories.py", "napi", "napi", "--registry", str(self.config),
        ]):
            with contextlib.redirect_stdout(output):
                self.assertEqual(refresh_repositories.main(), 0)
        self.assertEqual(output.getvalue().count("UPDATED:"), 1)

    def test_cli_missing_files_and_modes(self):
        code, output = self.run_checker(self.root / "missing.md", "--repo", self.root)
        self.assertEqual(code, 2, output)
        self.make_repo("napi")
        code, output = self.run_checker(self.doc(["napi"]), "--repo", self.configured["napi"][2])
        self.assertEqual(code, 2, output)
        self.assertIn("requires --registry", output)

    def test_checkout_mutation_during_check_is_incomplete(self):
        _, _, local, _ = self.make_repo("napi")
        original = check_staleness.changed_commits

        def mutate(*args):
            result = original(*args)
            (local / "src/api.txt").write_text("unexpected edit")
            return result

        with patch.object(check_staleness, "changed_commits", side_effect=mutate):
            code, output = self.run_checker(self.doc(["napi"]), "--registry", self.config)
        self.assertEqual(code, 2, output)
        self.assertIn("changed after refresh", output)

    def test_real_cli_preserves_verification_metadata(self):
        self.make_repo("napi")
        doc = self.doc(["napi"])
        doc_before = doc.read_text()
        config_before = self.config.read_text()
        before_files = set(self.root.iterdir())
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "check_staleness.py"),
             str(doc), "--registry", str(self.config)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("UPDATED:", result.stdout)
        self.assertIn("DOCUMENT:", result.stdout)
        self.assertEqual(doc.read_text(), doc_before)
        self.assertEqual(self.config.read_text(), config_before)
        self.assertEqual(set(self.root.iterdir()), before_files)
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "refresh_repositories.py"),
             "napi", "--registry", str(self.config)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("UPDATED:", result.stdout)

    def test_merge_options_do_not_squash_or_stash(self):
        _, writer, local, _ = self.make_repo("napi")
        self.git(local, "config", "branch.main.mergeOptions", "--squash")
        self.git(local, "config", "merge.autoStash", "true")
        target = self.commit(writer)
        self.assertEqual(refresh(registry(self.config)["napi"]), target)
        self.assertEqual("", self.git(local, "status", "--porcelain"))
        self.assertEqual("", self.git(local, "stash", "list"))

    def test_missing_dependency_reports_error_exit_code(self):
        result = subprocess.run(
            [sys.executable, "-S", str(SCRIPTS / "check_staleness.py"), "--help"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("PyYAML is required", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
