"""Shared code-reference parsing and safe refresh of configured repositories."""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:
    print(
        "error: PyYAML is required; install the plugin's requirements.txt "
        "with python -m pip install -r <plugin-root>/requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


class DocumentationError(Exception):
    """Invalid documentation/configuration or an unsuccessful repository operation."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of silently replacing configuration."""


def unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode) -> dict:
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise DocumentationError("YAML mapping keys must be strings")
        if key in mapping:
            raise DocumentationError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def load_mapping(text: str, location: Path) -> dict:
    try:
        value = yaml.load(text, Loader=UniqueKeyLoader)
    except (yaml.YAMLError, ValueError) as exc:
        raise DocumentationError(f"{location}: invalid YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise DocumentationError(f"{location}: expected a YAML mapping")
    return value


def read_mapping(path: Path) -> dict:
    try:
        return load_mapping(path.read_text(encoding="utf-8"), path)
    except (OSError, UnicodeError) as exc:
        raise DocumentationError(f"{path}: {exc}") from exc


def frontmatter(doc: Path) -> dict:
    try:
        lines = doc.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise DocumentationError(f"{doc}: {exc}") from exc
    if not lines or lines[0].strip() != "---":
        raise DocumentationError(f"{doc}: missing opening frontmatter '---'")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return load_mapping("\n".join(lines[1:i]), doc)
    raise DocumentationError(f"{doc}: missing closing frontmatter '---'")


def nonempty_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DocumentationError(f"{field}: expected a non-empty string")
    return value


@dataclass(frozen=True)
class CodeReference:
    repository: str
    paths: list[str]
    commit: str


def reference(value: dict, repository: str) -> CodeReference:
    paths = value.get("paths")
    if not isinstance(paths, list) or not paths:
        raise DocumentationError("code reference requires a non-empty list of paths")
    for path in paths:
        nonempty_string(path, "code reference path")
        if (
            path.startswith(("/", ":", "\\"))
            or "\\" in path
            or ".." in path.split("/")
            or re.match(r"^[A-Za-z]:", path)
        ):
            raise DocumentationError(f"expected a repo-relative path/glob: {path}")
    verified = value.get("verified_at")
    if not isinstance(verified, dict):
        raise DocumentationError("code reference requires verified_at")
    commit = nonempty_string(verified.get("commit"), "verified_at.commit")
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", commit):
        raise DocumentationError("verified_at.commit must be a Git commit SHA")
    verified_date = verified.get("date")
    try:
        if not isinstance(verified_date, (str, date)) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", str(verified_date)
        ):
            raise ValueError("expected YYYY-MM-DD")
        date.fromisoformat(str(verified_date))
    except ValueError as exc:
        raise DocumentationError("verified_at.date must be YYYY-MM-DD") from exc
    nonempty_string(verified.get("by"), "verified_at.by")
    return CodeReference(repository, paths, commit)


def code_references(doc: Path) -> list[CodeReference]:
    fm = frontmatter(doc)
    if "sources" in fm or "verified_at" in fm:
        raise DocumentationError(
            f"{doc}: sources and top-level verified_at are not supported; use code_references"
        )
    values = fm.get("code_references")
    if not isinstance(values, list) or not values:
        raise DocumentationError(f"{doc}: code_references must be a non-empty list")
    result = []
    for value in values:
        if not isinstance(value, dict):
            raise DocumentationError(f"{doc}: code reference must be a mapping")
        repository = nonempty_string(value.get("repository"), "repository")
        if any(item.repository == repository for item in result):
            raise DocumentationError(f"{doc}: duplicate repository reference: {repository}")
        result.append(reference(value, repository))
    return result


@dataclass(frozen=True)
class Repository:
    remote: str
    authoritative_branch: str
    local: Path


def registry(path: Path, override: Path | None = None) -> dict[str, Repository]:
    values = read_mapping(path).get("repositories")
    if not isinstance(values, dict) or not values:
        raise DocumentationError(f"{path}: repositories must be a non-empty mapping")
    local_overrides = {}
    if override is not None:
        local_overrides = read_mapping(override).get("repositories")
        if not isinstance(local_overrides, dict):
            raise DocumentationError(f"{override}: repositories must be a mapping")
        for name, value in local_overrides.items():
            if name not in values:
                raise DocumentationError(f"{override}: unknown repository: {name}")
            if not isinstance(value, dict) or set(value) != {"local"}:
                raise DocumentationError(f"{override}: overrides may only set local")
    result = {}
    for name, value in values.items():
        nonempty_string(name, "repository ID")
        if not isinstance(value, dict):
            raise DocumentationError(f"{path}: repository {name} must be a mapping")
        if set(value) != {"remote", "authoritative_branch", "local"}:
            raise DocumentationError(
                f"{path}: {name} requires only remote, authoritative_branch, local"
            )
        remote = nonempty_string(value.get("remote"), f"{name}.remote")
        branch = nonempty_string(
            value.get("authoritative_branch"), f"{name}.authoritative_branch"
        )
        local_value = local_overrides.get(name, value).get("local")
        local = Path(nonempty_string(local_value, f"{name}.local")).expanduser()
        base = (
            override.parent if override is not None and name in local_overrides else path.parent
        )
        result[name] = Repository(remote, branch, (base / local).resolve())
    return result


def git(repo: Path, *args: str, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DocumentationError(f"{repo}: git operation failed: {exc}") from exc
    if result.returncode not in allowed:
        raise DocumentationError(
            f"{repo}: git {' '.join(args)} failed: "
            f"{result.stderr.strip() or result.stdout.strip() or result.returncode}"
        )
    return result


def checkout_root(repo: Path) -> None:
    root = Path(git(repo, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if root != repo.resolve():
        raise DocumentationError(f"{repo}: local must name the checkout root, not a subdirectory")


def require_clean_branch(repo: Repository) -> None:
    branch = git(repo.local, "symbolic-ref", "--quiet", "--short", "HEAD").stdout.strip()
    if branch != repo.authoritative_branch:
        raise DocumentationError(
            f"{repo.local}: expected branch {repo.authoritative_branch}, found {branch}; "
            "will not switch branches"
        )
    if git(repo.local, "status", "--porcelain", "--untracked-files=all").stdout:
        raise DocumentationError(f"{repo.local}: checkout is dirty; will not stash or discard edits")


def refresh(repo: Repository) -> str:
    checkout_root(repo.local)
    git(repo.local, "check-ref-format", f"refs/heads/{repo.authoritative_branch}")
    remote_urls = [
        git(repo.local, "remote", "get-url", name).stdout.strip()
        for name in git(repo.local, "remote").stdout.splitlines()
    ]
    if repo.remote not in remote_urls:
        raise DocumentationError(f"{repo.local}: configured remote does not match a checkout remote")
    require_clean_branch(repo)
    git(
        repo.local, "fetch", "--no-tags", "--no-recurse-submodules", "--",
        repo.remote, f"refs/heads/{repo.authoritative_branch}",
    )
    target = git(repo.local, "rev-parse", "--verify", "FETCH_HEAD^{commit}").stdout.strip()
    require_clean_branch(repo)
    if git(repo.local, "merge-base", "--is-ancestor", "HEAD", target, allowed=(0, 1)).returncode:
        raise DocumentationError(
            f"{repo.local}: local-only or divergent commits; will not reset or rebase"
        )
    git(repo.local, "merge", "--ff-only", "--no-edit", "--no-autostash", "--no-squash", target)
    require_clean_branch(repo)
    if git(repo.local, "rev-parse", "HEAD").stdout.strip() != target:
        raise DocumentationError(f"{repo.local}: checkout changed during refresh")
    return target


def changed_commits(repo: Path, item: CodeReference, target: str) -> list[str]:
    verified = git(repo, "rev-parse", "--verify", f"{item.commit}^{{commit}}").stdout.strip()
    if git(repo, "merge-base", "--is-ancestor", verified, target, allowed=(0, 1)).returncode:
        raise DocumentationError(f"{repo}: verified commit {item.commit} is not an ancestor of {target}")
    output = git(repo, "log", "--oneline", f"{verified}..{target}", "--", *item.paths).stdout
    return output.splitlines()
