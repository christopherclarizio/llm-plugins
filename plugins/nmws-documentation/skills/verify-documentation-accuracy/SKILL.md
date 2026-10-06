---
name: verify-documentation-accuracy
description: Checks documentation claims against current source and product evidence. Use for deep grounding, stale-document repair, or preparation for human review. Reports supported, contradicted, and unresolved claims, and proposes warranted corrections or verification updates without automatically changing the corpus or promoting trust.
---

# Verify documentation accuracy

A fresh document can be wrong; a stale document can still be correct.
Verify claims, not merely the existence of named symbols.

## Before starting

Require `$NMWS_DOCS_CORPUS_ROOT` or a user-provided corpus root.
Use [Helper commands](../../reference/helpers.md) for plugin location, Git/uv
requirements, and source access. Never put real evidence into bundled examples.

## Assess the document

1. **Identify claims.** Read the whole document and retain its original contents.
   Include rationale, negative claims, product behavior, limitations, and
   cross-repository relationships, not just entry points.
2. **Establish the source baseline.** Run `check_staleness.py` for selected documents
   using the registry and local override. Reuse session SHAs only while checkouts
   remain unchanged and clean. Refresh newly discovered repositories once.
   Report failed refreshes as incomplete/not confirmed current and preserve known
   results; do not repair or substitute checkouts.
3. **Re-derive the claims.** Inspect current source and verify that reference paths
   cover the evidence. Changed areas are a starting point, not a reason to skip
   other claims when advancing verification metadata. Product workflows and
   historical motivation need separate evidence or knowledgeable confirmation.
   Distinguish authoritative-branch behavior, task-branch differences, and
   compatibility at a product release.
4. **Report the assessment.** Use a table with claim, status (`supported`,
   `contradicted`, `unresolved`), evidence (repository, file/symbol/line, checked
   SHA, or non-code evidence), and proposed action. Explain contradictions and
   missing evidence explicitly. Report grounding completeness, trust, and
   freshness separately; unresolved claims prevent an unqualified verified result.

## When an update is warranted

Prepare a complete correction/metadata diff. Advance a repository's `verified_at`
only after checking its entire contribution and correcting contradictions in the
proposal. Record the actual examined commit, current date, and `by: agent`;
leave unchecked entries unchanged. Removing an unsupported claim is a correction
requiring approval, not a way to hide uncertainty.

Preserve `human-reviewed` only when the body and evidence scope are unchanged.
Substantive agent corrections downgrade it to `agent-generated`, or `draft` if
material grounding gaps remain.

Use the [Accuracy-verification workflow](../../reference/proposal-workflow.md#accuracy-verification)
to validate, request exact-diff approval, and apply safely. A request to verify
does not authorize changes, commits, or pushes.

## When human review is requested

Present the exact final document and evidence report. Require explicit acceptance
of its full scope, including corrections, with no material unresolved claims.
Approval to save a diff is **not** confirmation of human review.

Ask for the reviewer's identity; product documents need someone with product
knowledge. Promote to `human-reviewed` only after acceptance. Name a person in
`verified_at.by` only for contributions they actually verified; one named verifier
does not automatically promote the document.

## References

- [Helper commands and source safety](../../reference/helpers.md)
- [Accuracy-verification workflow](../../reference/proposal-workflow.md#accuracy-verification)
- [Frontmatter contract](../../reference/frontmatter-schema.md)
- [Trust and staleness](../../reference/staleness-convention.md)
- [Repository configuration](../../reference/repository-registry.md)
