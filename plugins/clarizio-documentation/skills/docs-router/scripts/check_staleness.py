#!/usr/bin/env python3
"""Flag whether a documentation file's source anchors have drifted since it was verified.

Reads the doc's YAML frontmatter (`sources` and `verified_at.commit`) and runs
`git log <commit>..HEAD -- <sources>` against the code repository the doc describes.
Empty output means fresh; non-empty means the described code has changed since the doc
was last checked, so the doc is possibly stale.

Usage:
    check_staleness.py <doc.md> --repo <path-to-code-repo>

Exit codes: 0 fresh, 1 stale, 2 error.

Intentionally dependency-free: the frontmatter parser handles only the small, controlled
schema in reference/frontmatter-schema.md rather than pulling in a YAML library.
"""

import argparse
import subprocess
import sys
from pathlib import Path


class FrontmatterError(Exception):
    """The doc is missing or has malformed frontmatter."""


def read_frontmatter_lines(doc: Path) -> list[str]:
    """Return the raw lines between the opening and closing `---` fences."""
    text = doc.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FrontmatterError(f"{doc}: no frontmatter (missing opening '---')")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    raise FrontmatterError(f"{doc}: unterminated frontmatter (missing closing '---')")


def parse_anchors(fm_lines: list[str]) -> tuple[list[str], str | None]:
    """Extract `sources` (list) and `verified_at.commit` from frontmatter lines."""
    sources: list[str] = []
    commit: str | None = None
    in_sources = False
    in_verified = False

    for raw in fm_lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        top_level = raw == raw.lstrip()

        if top_level:
            in_sources = stripped.startswith("sources:")
            in_verified = stripped.startswith("verified_at:")
            if in_sources and "[" in stripped:  # inline: sources: [a, b]
                inline = stripped.split(":", 1)[1].strip().strip("[]")
                sources.extend(
                    item.strip().strip("'\"") for item in inline.split(",") if item.strip()
                )
                in_sources = False
            continue

        if in_sources and stripped.startswith("- "):
            sources.append(stripped[2:].strip().strip("'\""))
        elif in_verified and stripped.startswith("commit:"):
            commit = stripped.split(":", 1)[1].strip().strip("'\"")

    return sources, commit


def changed_commits(repo: Path, commit: str, sources: list[str]) -> list[str]:
    """Return one-line log entries for commits touching `sources` since `commit`."""
    result = subprocess.run(
        ["git", "-C", str(repo), "log", "--oneline", f"{commit}..HEAD", "--", *sources],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git log failed")
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("doc", type=Path, help="Path to the documentation markdown file.")
    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Path to the code repository the doc's `sources` are relative to.",
    )
    args = parser.parse_args()

    if not args.doc.is_file():
        print(f"error: doc not found: {args.doc}", file=sys.stderr)
        return 2
    if not (args.repo / ".git").exists():
        print(f"error: not a git repo: {args.repo}", file=sys.stderr)
        return 2

    try:
        sources, commit = parse_anchors(read_frontmatter_lines(args.doc))
    except FrontmatterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not sources:
        print(f"error: {args.doc}: frontmatter has no `sources`", file=sys.stderr)
        return 2
    if not commit:
        print(f"error: {args.doc}: frontmatter has no `verified_at.commit`", file=sys.stderr)
        return 2

    try:
        changed = changed_commits(args.repo, commit, sources)
    except RuntimeError as exc:
        print(f"error: git failed ({exc}); is {commit} present in {args.repo}?", file=sys.stderr)
        return 2

    if not changed:
        print(f"OK: no changes to sources since {commit} — doc is fresh.")
        return 0

    print(f"STALE: {len(changed)} commit(s) touched this doc's sources since {commit}:")
    for line in changed:
        print(f"  {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
