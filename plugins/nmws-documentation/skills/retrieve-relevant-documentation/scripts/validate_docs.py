#!/usr/bin/env -S uv run --locked --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["PyYAML>=6.0.2,<7", "markdown-it-py>=3,<4"]
# ///
"""Validate a corpus's code/ and product/ Markdown documents without accessing Git.

Exit codes: 0 valid (possibly warnings), 1 invalid documents, 2 configuration/read error.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from repositories import DocumentationError, code_references, frontmatter, registry

try:
    from markdown_it import MarkdownIt
except ModuleNotFoundError:
    print(
        "error: markdown-it-py is required; run the helper with "
        "uv run --locked --script <helper-path> [arguments] "
        "so uv manages its dependencies",
        file=sys.stderr,
    )
    raise SystemExit(2)


TIERS = {
    "code": ("architecture", "subsystem", "component"),
    "product": ("overview", "feature", "workflow"),
}
SECTIONS = {
    "code": (
        "Purpose & scope", "Concept", "Key entry points",
        "Complicated / confusing things", "Constraints & historical rationale",
        "Drill down / see also",
    ),
    "product": (
        "Purpose & scope", "What it is", "How it's used", "Where it fits",
        "Known limitations & sharp edges", "Implemented by", "Drill down / see also",
    ),
}
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FIELDS = {
    "id", "title", "description", "tree", "tier", "trust", "code_references",
    "parent", "children", "related", "keywords",
}
MARKDOWN = MarkdownIt()


@dataclass(frozen=True)
class Diagnostic:
    path: Path
    field: str
    message: str
    warning: bool = False


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.anchors.add(values["id"])
        if tag == "a" and values.get("name"):
            self.anchors.add(values["name"])
        for key in ("href", "src"):
            if values.get(key):
                self.links.append(values[key])


def markdown_content(text: str) -> tuple[dict[str, str], list[str], set[str], list[str]]:
    tokens = MARKDOWN.parse(text)
    sections: dict[str, str] = {}
    links: list[str] = []
    anchors: set[str] = set()
    fences: list[str] = []
    slug_counts: dict[str, int] = {}
    current = None
    html = HTMLLinks()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            title = tokens[index + 1].content
            plain_title = "".join(
                child.content for child in tokens[index + 1].children or []
                if child.type in ("text", "code_inline")
            )
            slug = re.sub(r"[^\w\- ]", "", plain_title.lower()).replace(" ", "-")
            count = slug_counts.get(slug, 0)
            slug_counts[slug] = count + 1
            anchors.add(f"{slug}-{count}" if count else slug)
            if token.tag == "h2":
                current = title
                sections.setdefault(title, "")
        elif token.type == "inline":
            if current is not None and (index == 0 or tokens[index - 1].type != "heading_open"):
                sections[current] += token.content + "\n"
            for child in token.children or []:
                if child.type == "link_open":
                    links.append(child.attrGet("href") or "")
                elif child.type == "image":
                    links.append(child.attrGet("src") or "")
                elif child.type == "html_inline":
                    html.feed(child.content)
        elif token.type == "html_block":
            html.feed(token.content)
        elif token.type in ("fence", "code_block"):
            fences.append(token.content)
            if current is not None:
                sections[current] += token.content
    anchors.update(html.anchors)
    links.extend(html.links)
    return sections, links, anchors, fences


def body(text: str) -> str:
    lines = text.splitlines()
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1:])
    raise DocumentationError("missing closing frontmatter")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DocumentationError(f"{path}: {exc}") from exc


def validate(corpus: Path, registry_path: Path) -> list[Diagnostic]:
    corpus = corpus.resolve()
    repositories = registry(registry_path)
    paths = sorted(
        path for tree in TIERS for path in (corpus / tree).rglob("*.md")
    )
    if not paths:
        raise DocumentationError(f"{corpus}: no documents in code/ or product/")
    diagnostics: list[Diagnostic] = []
    documents: dict[Path, dict] = {}
    ids: dict[str, Path] = {}

    def report(path, field, message, warning=False):
        diagnostics.append(Diagnostic(path, field, message, warning))

    for path in paths:
        contents = read_text(path)
        try:
            fm = frontmatter(path)
            text = body(contents)
        except DocumentationError as exc:
            report(path, "frontmatter", str(exc))
            continue
        documents[path] = fm
        for field in fm.keys() - FIELDS:
            report(path, field, "unknown frontmatter field")
        for field in ("id", "title", "description", "tree", "tier", "trust"):
            if not isinstance(fm.get(field), str) or not fm[field].strip():
                report(path, field, "requires a non-empty string")
        doc_id = fm.get("id")
        if isinstance(doc_id, str):
            if not SLUG.fullmatch(doc_id):
                report(path, "id", "must be a stable kebab-case slug")
            if doc_id in ids:
                report(path, "id", f"duplicate {doc_id!r}, also in {ids[doc_id]}")
            else:
                ids[doc_id] = path
        tree = fm.get("tree")
        if not isinstance(tree, str) or tree not in TIERS:
            report(path, "tree", "must be code or product")
        else:
            if path.relative_to(corpus).parts[0] != tree:
                report(path, "tree", f"document must live under {tree}/")
            if fm.get("tier") not in TIERS[tree]:
                report(path, "tier", f"expected one of {', '.join(TIERS[tree])}")
        if fm.get("trust") not in ("draft", "agent-generated", "human-reviewed"):
            report(path, "trust", "must be draft, agent-generated, or human-reviewed")
        if "parent" in fm and (
            not isinstance(fm["parent"], str) or not SLUG.fullmatch(fm["parent"])
        ):
            report(path, "parent", "must be a document ID")
        for field in ("children", "related", "keywords"):
            if field not in fm:
                continue
            values = fm[field]
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value.strip() for value in values
            ):
                report(path, field, "must be a list of non-empty strings")
            elif len(values) != len(set(values)):
                report(path, field, "must not contain duplicates")
        try:
            for ref in code_references(path):
                if ref.repository not in repositories:
                    report(path, "code_references", f"unknown repository ID: {ref.repository}")
        except DocumentationError as exc:
            report(path, "code_references", str(exc))

        sections, links, _, fences = markdown_content(text)
        if isinstance(tree, str) and tree in SECTIONS:
            for section in SECTIONS[tree]:
                if not sections.get(section, "").strip():
                    report(path, "body", f"missing or empty section: {section}")
        scope = re.sub(r"[*_`]", "", sections.get("Purpose & scope", "")).lower()
        if not re.search(r"\b(?:does\s+not|do\s+not|not\s+covered|out\s+of\s+scope|excludes?)\b", scope):
            report(path, "Purpose & scope", "state explicitly what the document does not cover")
        if re.search(r"<(?:stable-kebab-slug|Human Readable Title|path/or/glob|sha|id)[^>]*>", text):
            report(path, "body", "unfilled template placeholder")
        if sum(len(fence.splitlines()) for fence in fences) > 20:
            report(path, "altitude", "more than 20 lines of code; review for code-restating trivia", True)
        if isinstance(tree, str) and tree in TIERS:
            related = fm.get("related", [])
            if isinstance(related, list) and not related:
                report(path, "related", "add a counterpart link when one exists; do not invent one", True)
        for link in links:
            try:
                url = urlsplit(link)
            except ValueError as exc:
                report(path, "link", f"invalid destination {link!r}: {exc}")
                continue
            if url.scheme in ("http", "https", "mailto", "tel") or (not url.scheme and url.netloc):
                continue
            link_path = unquote(url.path)
            if url.scheme or link_path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", link_path):
                report(path, "link", f"use a relative path or supported URL: {link}")
                continue
            target = (path.parent / link_path).resolve() if link_path else path
            if not target.exists():
                report(path, "link", f"missing target: {link}")
            elif url.fragment and target.is_file() and target.suffix.lower() == ".md":
                target_text = read_text(target)
                if target_text.startswith("---\n"):
                    target_text = body(target_text)
                _, _, anchors, _ = markdown_content(target_text)
                if unquote(url.fragment) not in anchors:
                    report(path, "link", f"missing heading/anchor: {link}")

    for path, fm in documents.items():
        for field in ("parent", "children", "related"):
            values = [fm[field]] if field == "parent" and field in fm else fm.get(field, [])
            if not isinstance(values, list):
                continue
            for value in values:
                if not isinstance(value, str):
                    continue
                if value not in ids:
                    report(path, field, f"unresolved document ID: {value}")
                    continue
                target_path = ids[value]
                target = documents[target_path]
                if target_path == path:
                    report(path, field, "must not link to itself")
                if field == "related":
                    continue
                tree = fm.get("tree")
                tier = fm.get("tier")
                target_tier = target.get("tier")
                if not isinstance(tree, str) or tree not in TIERS:
                    continue
                if target.get("tree") != tree:
                    report(path, field, "hierarchy must stay within one tree")
                elif tier in TIERS[tree] and target_tier in TIERS[tree]:
                    delta = TIERS[tree].index(target_tier) - TIERS[tree].index(tier)
                    if (field == "parent" and delta >= 0) or (field == "children" and delta <= 0):
                        report(path, field, "parent must be coarser; children must be finer")
                if field == "children" and target.get("parent") != fm.get("id"):
                    report(path, field, f"{value} must name this document as parent")
                if field == "parent":
                    children = target.get("children", [])
                    if not isinstance(children, list) or fm.get("id") not in children:
                        report(path, field, f"{value} must list this document in children")
    return diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--registry", type=Path, help="Defaults to <corpus-root>/repositories.yaml")
    parser.add_argument("--strict", action="store_true", help="Treat heuristic warnings as failures")
    args = parser.parse_args()
    try:
        diagnostics = validate(
            args.corpus_root, args.registry or args.corpus_root / "repositories.yaml"
        )
    except DocumentationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for item in diagnostics:
        print(f"{'WARNING' if item.warning else 'ERROR'}: {item.path}: {item.field}: {item.message}")
    errors = sum(not item.warning for item in diagnostics)
    warnings = sum(item.warning for item in diagnostics)
    print(f"VALIDATION: {errors} error(s), {warnings} warning(s)")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
