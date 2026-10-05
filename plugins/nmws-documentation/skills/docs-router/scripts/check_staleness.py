#!/usr/bin/env python3
"""Check documents' code references, refreshing registered repositories first.

Usage: check_staleness.py <doc> [<doc> ...] --registry <repositories.yaml>
Exit codes: 0 fresh, 1 stale, 2 error/incomplete (even if other references are stale).
"""

import argparse
import sys
from pathlib import Path

from repositories import (
    DocumentationError,
    changed_commits,
    code_references,
    git,
    refresh,
    registry,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("docs", type=Path, nargs="+")
    parser.add_argument("--registry", type=Path, required=True, help="Registry; refreshes checkouts.")
    parser.add_argument("--override", type=Path, help="Optional registry file overriding only local paths.")
    args = parser.parse_args()

    errors = False
    stale = False
    documents = {}
    for doc in args.docs:
        try:
            items = code_references(doc)
            documents[doc] = items
        except DocumentationError as exc:
            print(f"ERROR: {doc}: {exc}", file=sys.stderr)
            errors = True

    repositories = {}
    registry_error = None
    try:
        repositories = registry(args.registry, args.override)
    except DocumentationError as exc:
        registry_error = str(exc)
        print(f"ERROR: {exc}", file=sys.stderr)
        errors = True

    revisions: dict[str, str] = {}
    refresh_errors: dict[str, str] = {}
    needed = dict.fromkeys(
        item.repository for items in documents.values() for item in items
    )
    for name in needed:
        try:
            if registry_error is not None:
                raise DocumentationError(registry_error)
            if name not in repositories:
                raise DocumentationError(f"unknown repository ID: {name}")
            repo = repositories[name]
            revisions[name] = refresh(repo)
            print(f"UPDATED: {name} {repo.authoritative_branch} @ {revisions[name]} ({repo.local})")
        except DocumentationError as exc:
            refresh_errors[name] = str(exc)
            errors = True
            print(f"ERROR: {name}: not confirmed current: {exc}", file=sys.stderr)

    for doc, items in documents.items():
        doc_error = False
        doc_stale = False
        for item in items:
            name = item.repository
            try:
                if name in refresh_errors:
                    raise DocumentationError(f"not confirmed current: {refresh_errors[name]}")
                repo_path = repositories[name].local
                target = revisions[name]
                changed = changed_commits(repo_path, item, target)
                working_changes = git(
                    repo_path, "status", "--porcelain", "--untracked-files=all", "--", *item.paths
                ).stdout
                if git(repo_path, "rev-parse", "HEAD").stdout.strip() != target:
                    raise DocumentationError("checkout changed during freshness check")
                if working_changes:
                    raise DocumentationError("referenced working files changed after refresh")
                is_stale = bool(changed)
                doc_stale |= is_stale
                print(
                    f"{'STALE' if is_stale else 'OK'}: {doc} [{name}] "
                    f"verified {item.commit}, checked {target}"
                )
                for entry in changed:
                    print(f"  {entry}")
            except DocumentationError as exc:
                doc_error = True
                print(f"ERROR: {doc} [{name}]: {exc}", file=sys.stderr)
        errors |= doc_error
        stale |= doc_stale
        print(f"DOCUMENT: {doc}: {'incomplete' if doc_error else 'stale' if doc_stale else 'fresh'}")
    return 2 if errors else 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
