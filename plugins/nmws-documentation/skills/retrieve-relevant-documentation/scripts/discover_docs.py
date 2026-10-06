#!/usr/bin/env -S uv run --locked --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Return bounded, metadata-only documentation candidates as JSON.

Exit codes: 0 successful (including no matches), 2 configuration/read/metadata error.
No repository access, body reads, saved index, or freshness assertions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from repositories import TIERS, DocumentationError, frontmatter, nonempty_string


MAX_LIMIT = 20
STOP_WORDS = frozenset(
    "a an and are as at be before by do does for from how i in is it of on or "
    "the this to what when where which with".split()
)


def words(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[^\W_]+", text.casefold()))


def metadata(path: Path, corpus: Path) -> dict:
    fm = frontmatter(path)
    result = {"path": path.relative_to(corpus).as_posix()}
    for field in ("id", "title", "description", "tree", "tier", "trust"):
        result[field] = nonempty_string(fm.get(field), f"{path}: {field}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", result["id"]):
        raise DocumentationError(f"{path}: id must be a stable kebab-case slug")
    tree = result["tree"]
    if tree not in TIERS or path.relative_to(corpus).parts[0] != tree:
        raise DocumentationError(f"{path}: tree must match code/ or product/")
    if result["tier"] not in TIERS[tree]:
        raise DocumentationError(f"{path}: invalid {tree} tier: {result['tier']}")
    if result["trust"] not in ("draft", "agent-generated", "human-reviewed"):
        raise DocumentationError(f"{path}: invalid trust: {result['trust']}")
    for field in ("keywords", "children", "related"):
        values = fm.get(field, [])
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise DocumentationError(f"{path}: {field} must be a list of non-empty strings")
        result[field] = values
    result["parent"] = (
        nonempty_string(fm["parent"], f"{path}: parent") if "parent" in fm else None
    )
    return result


def discover(
    corpus: Path, query: str = "", mode: str = "focused", limit: int = 5,
    tree: str | None = None, doc_id: str | None = None,
) -> dict:
    if mode not in ("focused", "orientation"):
        raise DocumentationError("mode must be focused or orientation")
    if not 1 <= limit <= MAX_LIMIT:
        raise DocumentationError(f"limit must be between 1 and {MAX_LIMIT}")
    if tree is not None and tree not in TIERS:
        raise DocumentationError("tree must be code or product")
    phrase = words(query)
    terms = set(phrase) - STOP_WORDS
    if doc_id is None and not terms and (mode == "focused" or query.strip()):
        raise DocumentationError("supply a meaningful query, --id, or query-free orientation")
    corpus = corpus.expanduser().resolve()
    if not corpus.is_dir():
        raise DocumentationError(f"{corpus}: corpus root is not a directory")
    paths = sorted(path for name in TIERS for path in (corpus / name).rglob("*.md"))
    if not paths:
        raise DocumentationError(f"{corpus}: no documents in code/ or product/")
    ranked = []
    ids = {}
    for path in paths:
        doc = metadata(path, corpus)
        if doc["id"] in ids:
            raise DocumentationError(
                f"{path}: duplicate ID {doc['id']!r}, also in {ids[doc['id']]}"
            )
        ids[doc["id"]] = path
        if (tree is not None and doc["tree"] != tree) or (
            doc_id is not None and doc["id"] != doc_id
        ):
            continue
        fields = {
            "id": [doc["id"]], "title": [doc["title"]],
            "keywords": doc["keywords"], "description": [doc["description"]],
        }
        matches = {
            field: terms & {term for value in values for term in words(value)}
            for field, values in fields.items()
        }
        matched = set().union(*matches.values())
        exact = [
            field for field in ("id", "title", "keywords")
            if phrase and any(words(value) == phrase for value in fields[field])
        ]
        if doc_id is None and terms and not matched:
            continue
        score = sum(
            len(matches[field]) * weight
            for field, weight in (("id", 8), ("title", 6), ("keywords", 4), ("description", 1))
        )
        altitude = TIERS[doc["tree"]].index(doc["tier"])
        exact_rank = max(
            (weight for field, weight in (("id", 3), ("title", 2), ("keywords", 1)) if field in exact),
            default=0,
        )
        relevance = (exact_rank, len(matched), score)
        priority = (
            (altitude, *(-value for value in relevance))
            if mode == "orientation" else (*(-value for value in relevance), -altitude)
        )
        doc["match"] = {
            "exact_fields": exact, "matched_terms": sorted(matched), "score": score,
        }
        ranked.append((priority, doc["id"], doc["path"], doc))
    ranked.sort(key=lambda item: item[:3])
    return {
        "corpus_root": str(corpus), "query": query, "mode": mode,
        "scanned": len(paths), "matched": len(ranked), "limit": limit,
        "truncated": len(ranked) > limit,
        "candidates": [item[3] for item in ranked[:limit]],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--query", default="")
    parser.add_argument("--mode", choices=("focused", "orientation"), default="focused")
    parser.add_argument("--tree", choices=tuple(TIERS))
    parser.add_argument("--id", dest="doc_id", help="Resolve an exact document ID, including navigation links")
    parser.add_argument("--limit", type=int, default=5, help=f"Candidate count, 1-{MAX_LIMIT} (default: 5)")
    args = parser.parse_args()
    try:
        result = discover(
            args.corpus_root, args.query, args.mode, args.limit, args.tree, args.doc_id,
        )
    except DocumentationError as exc:
        print(json.dumps({"error": str(exc), "candidates": []}))
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
