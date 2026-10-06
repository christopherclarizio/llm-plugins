---
name: docs-verify
description: Re-derives a documentation file's claims from current configured source, reporting supported, contradicted, and unresolved claims. Use for deep grounding, stale-doc repair, or preparing a human review. Proposes evidence-backed corrections and per-repository verification updates; never equates freshness with correctness or automatically promotes trust.
---

# docs-verify

Deep grounding, not the cheap changed-path check. A fresh document can be wrong;
a stale document can still describe current behavior correctly.

## Setup

Resolve `PLUGIN_ROOT` from `CLAUDE_PLUGIN_ROOT`, otherwise this skill's location.
Require `$NMWS_DOCS_CORPUS_ROOT` or a user-provided corpus root. Bundled examples may be
read as illustrations, never updated with real source evidence. Git and `uv` are
prerequisites; [set-me-up](../set-me-up/SKILL.md) installs missing tools and configures
the corpus. Use `uv run --locked --script` for helpers as in `docs-router`; uv manages
Python and isolated dependencies. Surface missing tools or failed downloads.

## Procedure

1. **Read the whole document.** Identify its scope, all substantive assertions, and
   code references. Include rationale, negative claims, user behavior, limitations,
   and cross-repository relationships, not just named entry points. Record the original
   file contents for the eventual concurrency check.
2. **Establish the baseline.** Batch selected docs through `check_staleness.py` with
   the corpus registry and optional override, as in `docs-router`. Reuse unchanged,
   clean checked SHAs from this session instead of refreshing twice. If a referenced
   repository cannot refresh, report it as incomplete/not confirmed current; continue
   reporting known results, but never declare the document fully verified.
   If new dependencies emerge, resolve them through the registry and refresh once.
   Do not switch branches, reset, stash, discover, or repair checkouts.
3. **Re-derive every claim.** Read current source in the selected clean authoritative
   checkouts. Check behavior and invariants, not merely symbol existence. Inspect changed
   areas first, but do not skip unaffected claims when advancing a repository's
   verification commit. Verify that reference paths cover the actual evidence.
   Distinguish independent latest-main revisions from a compatible released product.
   Separate task-branch behavior from the documentation baseline.

   Report a claim table with: claim, status (`supported`, `contradicted`, `unresolved`),
   evidence (repository, relative file and symbol/line, checked SHA), and proposed action.
   Explain contradictions precisely. Missing access, product knowledge, or historical
   evidence is unresolved, never agreement. Product workflows and limitations need
   product evidence or confirmation by a knowledgeable person. Do not assert historical
   motivation just because present code would be consistent with it.
4. **Prepare corrections and metadata.** Propose a complete diff, not silent edits.
   Only advance a repository's `verified_at` after its entire contribution is grounded
   and any contradictions are corrected in the proposed text. Use the actual examined
   commit, current date, and actual verifier (`agent` for agent work). Leave unchecked
   entries unchanged. Unresolved claims prevent an unqualified verified result.
   Removing an unsupported assertion is a substantive correction requiring approval,
   not a way to hide uncertainty.

   Preserve `human-reviewed` for an unchanged body and unchanged evidentiary scope
   when only grounded metadata is updated; agent verification does not add human review.
   Substantive agent corrections to a human-reviewed document downgrade it to
   `agent-generated`, or `draft` if material grounding gaps remain.
5. **Validate, approve, and apply.** Follow `docs-capture`'s temporary-copy validation,
   exact-diff approval, source/target concurrency checks, and post-write validation.
   A verification request alone does not approve proposed changes. Report per-repository
   results, overall grounding completeness, trust, and freshness separately.
   Do not commit or push without separate authorization.
6. **Human-review gate, when requested.** Present the exact final document and evidence
   report to a human reviewer. Require explicit confirmation that they reviewed and
   accept its full scope, including corrections; approval to save an agent diff is not
   that confirmation. Product docs need someone with product knowledge. Ask for the
   reviewer's identity rather than inventing it. Promote to `human-reviewed` only after
   this acceptance and only with no material unresolved claims. Set a repository's
   `verified_at.by` to the person only if they actually verified that contribution.
   Trust is document-wide; one repository's named verifier never automatically promotes it.

## Reference

- [Capture workflow](../docs-capture/SKILL.md)
- [Write-loop contract](../../reference/write-loop.md)
- [Trust and staleness](../../reference/staleness-convention.md)
