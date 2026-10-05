#!/usr/bin/env python3
"""Refresh selected repositories without switching branches or discarding edits."""

import argparse
import sys
from pathlib import Path

from repositories import DocumentationError, refresh, registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repositories", nargs="+", help="Repository IDs to refresh.")
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--override", type=Path)
    args = parser.parse_args()
    try:
        configured = registry(args.registry, args.override)
    except DocumentationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = False
    for name in dict.fromkeys(args.repositories):
        try:
            if name not in configured:
                raise DocumentationError(f"unknown repository ID: {name}")
            repo = configured[name]
            sha = refresh(repo)
            print(f"UPDATED: {name} {repo.authoritative_branch} @ {sha} ({repo.local})")
        except DocumentationError as exc:
            errors = True
            print(f"ERROR: {name}: not confirmed current: {exc}", file=sys.stderr)
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
