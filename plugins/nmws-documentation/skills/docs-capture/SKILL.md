---
name: docs-capture
description: Graduates durable understanding from a completed investigation into a concrete, approval-gated documentation diff. Use after a meaningful docs-router miss, corrected assumption, or source-grounded re-derivation; also when explicitly asked to capture understanding. Deduplicates against the corpus, grounds references per repository, validates the proposal, and never writes or commits without approval.
---

# docs-capture

The write-loop entry point. Capture understanding that will prevent a future wrong
turn, not a transcript or a restatement of code.

## Trigger and destination

Use after a task yields a reusable mental model, relationship, invariant, rationale,
or corrected misconception. A router miss is a candidate, not sufficient evidence.
Skip trivial edits, already-covered discoveries, transient debugging notes, and
sessions without durable learning. Do not offer capture after every task. An explicit
request to document something permits preparation, not unsupported claims.

Resolve `PLUGIN_ROOT` from `CLAUDE_PLUGIN_ROOT` when available, otherwise from this
skill's location beneath the plugin root. Require an explicit `$NMWS_DOCS_CORPUS_ROOT`
or a corpus root provided by the user. **Do not fall back to bundled examples for
writes.** Source-derived documents and review/evaluation evidence belong only in the
private corpus or private local artifacts, never this public plugin repository.

Git, Python 3.9+, and the plugin's `requirements.txt` are required. Install missing
dependencies only when permitted; failures block validation rather than being skipped.

## Procedure

1. **Assess the learning.** Summarize the durable question answered and the discovery
   that makes capture worthwhile. Carry forward any router gap, document IDs used,
   source evidence, repository SHAs, and task-branch differences from the conversation.
   Do not create a saved lookup snapshot or a new frontmatter field for this handoff.
2. **Deduplicate.** Read corpus frontmatter under `code/` and `product/`, then bodies
   of likely overlaps and adjacent parents/counterparts. Prefer a surgical update to
   an existing document. If nothing adds durable value, say no capture is warranted.
   Do not generate an index or load the entire corpus's bodies.
3. **Ground against authoritative source.** Resolve repositories through the corpus's
   `repositories.yaml` and optional `repositories.local.yaml`; never discover, clone,
   or repair checkouts. Reuse a successful router refresh only if its checked SHAs
   and clean state are still unchanged. Otherwise refresh needed repositories once:
   ```sh
   python3 "${PLUGIN_ROOT}/skills/docs-router/scripts/refresh_repositories.py" \
     <repository-id> [<other-id> ...] --registry <corpus-root>/repositories.yaml
   ```
   Add `--override <corpus-root>/repositories.local.yaml` when it exists.
   Examine the source that establishes the proposed claims, including dependencies
   outside previously recorded paths. Refresh success alone is not evidence.
   Task-branch-only discoveries cannot be recorded as verified main behavior.
   Product behavior, user workflows, limitations, and historical motivations need
   their own evidence or knowledgeable human confirmation; do not invent them from code.
4. **Prepare the full diff.** Use the appropriate
   [code](../../templates/code-doc.template.md) or
   [product](../../templates/product-doc.template.md) template. Keep the selected
   tier's altitude: explain concepts, relationships, invariants, and why. Include
   concrete entry points, but not signature inventories or line-by-line summaries.
   Explicitly say what is not covered. Keep existing IDs stable.

   Fill `code_references` with narrowly scoped repository-relative paths covering
   all source-derived claims and independent verification metadata for each repository.
   For a new grounded doc, use the actual checked commit, current verification date,
   `by: agent`, and `trust: agent-generated`. Updating an existing doc's verification
   commit requires checking its **entire contribution from that repository**, not just
   the new paragraph; use `docs-verify` when needed. Never stamp unchecked repositories.
   Block persistence of unsupported new claims; an incomplete proposal may be shown as
   `draft`, clearly stating missing evidence, but does not receive fabricated metadata.
   If a substantive claim or its evidentiary scope changes in a `human-reviewed` doc,
   downgrade to `agent-generated` pending renewed human review.

   Update parent/children links together; link an existing other-tree counterpart
   through `related` and relative-path prose. Missing counterparts are not an excuse
   to invent documents. Cross-link procedures rather than absorbing how-tos.
5. **Validate before approval.** Materialize the proposal in a private temporary copy
   of the corpus, preserving relative paths and the registry (no source checkouts need
   copying). Apply the entire proposed diff there and run:
   ```sh
   python3 "${PLUGIN_ROOT}/skills/docs-router/scripts/validate_docs.py" \
     --corpus-root <temporary-corpus-root>
   ```
   Validation is offline and does not use checkout paths. Resolve every error caused
   by the proposal. Report pre-existing errors explicitly; do not claim the corpus
   passes while they remain. Review every altitude warning manually. Present the
   **exact validated diff**, affected document IDs, evidence/SHAs, trust changes, and
   any verification gaps for yes/no approval. Never ask an open-ended "what should I write?"
6. **Apply only the approved diff.** Approval must cover the concrete proposal.
   Before applying, compare target documents to their pre-proposal contents and check
   every consulted checkout with `git -C <checkout> rev-parse HEAD` and
   `git -C <checkout> status --porcelain --untracked-files=all`. A changed SHA, dirty
   checkout, or changed target invalidates the proposal: re-derive/revalidate and seek
   renewed approval rather than overwriting edits. Respect a rejection without writing.
   After applying, rerun validation in the real corpus and inspect the resulting diff.
   Report exact paths written and trust/freshness; surface any failure explicitly.
   Do not stage, commit, push, or promote trust without separate authorization.
   Remove only the temporary artifacts created for this proposal.

## Reference

- [Write-loop contract](../../reference/write-loop.md)
- [Frontmatter schema](../../reference/frontmatter-schema.md)
- [Trust and staleness](../../reference/staleness-convention.md)
- [Validation contract](../../reference/validation.md)
