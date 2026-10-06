---
name: capture-information-in-documentation
description: Captures reusable code and product understanding in corpus documents. Use after a substantive investigation yields a new mental model, invariant, relationship, or corrected misconception, or when explicitly asked to document something. Writes evidence-backed updates to the configured corpus.
---

# Capture understanding in documentation

Capture understanding that will prevent a future wrong turn, not a transcript
or a restatement of code.

## Before starting

Require `$NMWS_DOCS_CORPUS_ROOT` or a user-provided corpus root. Use
[Helper commands](../../reference/helpers.md) for the plugin location and uv-managed
execution. Git and uv are required. Write documents beneath the selected corpus
root. Real-source documents do not belong in the public plugin repository.

## Workflow

1. **Decide whether to capture.** Identify the durable question answered and what
   a future reader would otherwise misunderstand. Skip transient debugging notes,
   trivial edits, and already-covered discoveries. A retrieval miss alone does
   not justify capture; do not offer it after every task.
2. **Find its home.** Use `discover_docs.py` in `focused` mode, refine weak or
   truncated results, and read likely overlaps and adjacent parents/counterparts.
   Resolve navigation IDs with `--id`. Prefer updating an existing document;
   if nothing adds durable value, say no capture is warranted.
3. **Ground the discovery.** Resolve sources through the corpus registry and
   local override. Reuse session SHAs only while the checked repositories remain
   unchanged and clean; otherwise refresh the needed repositories once with
   `refresh_repositories.py`. Examine the code establishing each claim, including
   newly discovered dependencies. Separate task-branch behavior from authoritative
   branch behavior. Product workflows, limitations, and historical rationale need
   their own evidence or knowledgeable human confirmation, not inference from code.
4. **Draft the update.** Use the [code](../../templates/code-doc.template.md) or
   [product](../../templates/product-doc.template.md) template and the selected tier's
   level of detail. Explain concepts, relationships, invariants, and why; name useful
   entry points without restating signatures. State scope exclusions and preserve IDs.
   Update parent/children links together and link existing cross-tree counterparts.
   Link to procedures rather than absorbing how-tos; do not invent missing documents.
5. **Write and validate.** Follow the
   [Capture workflow](../../reference/proposal-workflow.md#capture): check for
   concurrent changes, write the complete update beneath the selected corpus root,
   and validate the corpus.
   Report the exact paths written and any remaining gaps or validation failures.

## Evidence and metadata

Keep `code_references` narrowly scoped but sufficient for all source-derived claims.
For a new grounded document, use `trust: agent-generated`. For each repository,
record the actual examined commit, current date, and `by: agent`.
Advancing an existing repository's verification commit requires checking its
**entire contribution to the document**, not just the added paragraph; use
[Verify](../verify-documentation-accuracy/SKILL.md) for claim assessment when needed.
Write resulting capture changes through the capture workflow.

Never stamp unchecked repositories or persist unsupported new claims. An incomplete
document may be saved as `draft` with explicit gaps, but no fabricated metadata.
Substantive changes to a `human-reviewed` document's claims or evidence scope require
downgrading to `agent-generated` pending renewed human review.

## References

- [Helper commands and source safety](../../reference/helpers.md)
- [Documentation update workflow](../../reference/proposal-workflow.md)
- [Frontmatter contract](../../reference/frontmatter-schema.md)
- [Trust and staleness](../../reference/staleness-convention.md)
- [Repository configuration](../../reference/repository-registry.md)
